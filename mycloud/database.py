#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

import os
import re
import asyncio
import aiofiles
from warnings import deprecated
from typing import Iterable, Any
from contextlib import asynccontextmanager
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, BigInteger, not_, exists
from sqlalchemy import func, select, delete, text, update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import and_, or_
from datetime import datetime
from settings import DB_URL, DB_POOL_SIZE, BASE_PATH
from common.writer_queue import writer_queue

Base = declarative_base()


async def write_worker():
    while True:
        writer, future = await writer_queue.get()
        try:
            result = await writer()
            if not future.done():
                future.set_result(result)
        except Exception as e:
            if not future.done():
                future.set_exception(e)
        finally:
            writer_queue.task_done()


async def _execute_in_queue(task_func):
    loop = asyncio.get_running_loop()
    future = loop.create_future()
    await writer_queue.put((task_func, future))
    return await future


class Database:
    engine = create_async_engine(DB_URL, echo=False, pool_size=DB_POOL_SIZE, max_overflow=DB_POOL_SIZE * 2, pool_timeout=30, pool_recycle=3600, pool_pre_ping=True)
    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    @classmethod
    async def get_session(cls) -> AsyncSession:
        return cls.session_factory()

    @classmethod
    async def init_db(cls):
        async with cls.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @classmethod
    async def dispose(cls):
        await cls.engine.dispose()


class DBExecutor:
    @staticmethod
    @asynccontextmanager
    async def session_scope():
        session: AsyncSession = await Database.get_session()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


class BaseQueryBuilder:
    def __init__(self, model):
        self.model = model
        self._select_columns = None
        self._conditions = []
        self._group_by = []
        self._order_by = []
        self._limit = None
        self._offset = None
        self._with_count = False
        self._distinct = False
        self._distinct_on = []
        self._joins = []
        self._exists = None
        self._having = []
        self._for_update = False
        self._for_update_opts = None

    def _parse_select_expr(self, expr_str: str):
        """
        内部方法：解析 select 字符串表达式，彻底屏蔽 func 导入
        支持:
        1. "name" -> Model.name
        2. "count(*)" -> func.count(text('*'))
        3. "count(1)" -> func.count(1)
        4. "sum(amount)" -> func.sum(Model.amount)
        5. "sum(amount) as total" -> func.sum(Model.amount).label("total")
        """
        expr_str = expr_str.strip()
        alias = None
        # 检查是否有 as 别名 (不区分大小写)
        if re.search(r'\s+as\s+', expr_str, re.IGNORECASE):
            parts = re.split(r'\s+as\s+', expr_str, flags=re.IGNORECASE)
            expr_str = parts[0].strip()
            alias = parts[1].strip()

        # 检查是否是函数调用，如 sum(amount) 或 count(*)
        match = re.match(r'^(\w+)\((.*)\)$', expr_str)
        if match:
            func_name = match.group(1).lower()
            arg = match.group(2).strip()

            # 处理参数
            if arg == '*':
                col_expr = func.count(text('*')) if func_name == 'count' else getattr(func, func_name)(text('*'))
            elif arg == '1':
                col_expr = func.count(1) if func_name == 'count' else getattr(func, func_name)(1)
            else:
                col_expr = getattr(func, func_name)(getattr(self.model, arg))
        else:
            col_expr = getattr(self.model, expr_str)

        # 应用别名
        if alias:
            return col_expr.label(alias)
        return col_expr

    # 查询指定的字段
    def select(self, *columns: str):
        '''
        1. 普通字段: await User.query().select("id", "name").all()
        2. 聚合查询: await User.query().select("status", "sum(amount) as total_amount", "count(*) as order_count").group_by("status").all()
        3. 兼容传对象: await User.query().select(User.id, func.max(User.age)).all() (高级用法)
        '''
        parsed_columns = []
        for c in columns:
            if isinstance(c, str):
                if " " in c or "(" in c:
                    parsed_columns.append(self._parse_select_expr(c))
                else:
                    parsed_columns.append(getattr(self.model, c))
            else:
                # 兼容直接传入 SQLAlchemy 表达式对象
                parsed_columns.append(c)
        self._select_columns = parsed_columns
        return self

    # where 条件
    def equal(self, **kwargs):
        '''
        rows = await User.query().equal(name="Tom").all()
        SELECT * FROM user WHERE name = 'Tom';
        '''
        for k, v in kwargs.items():
            self._conditions.append(getattr(self.model, k) == v)
        return self

    def not_equal(self, **kwargs):
        '''
        rows = await User.query().not_equal(status=0).all()
        SELECT * FROM user WHERE status != 0;
        '''
        for k, v in kwargs.items():
            self._conditions.append(getattr(self.model, k) != v)
        return self

    def like(self, **kwargs):
        '''
        await User.query().like(name="Tom").all()
        SELECT * FROM user WHERE name LIKE '%Tom%';
        '''
        for k, v in kwargs.items():
            if v:
                self._conditions.append(getattr(self.model, k).like(f"%{v}%"))
        return self

    def startLike(self, **kwargs):
        '''
        await User.query().like(name="Tom").all()
        SELECT * FROM user WHERE name LIKE 'Tom%';
        '''
        for k, v in kwargs.items():
            if v:
                self._conditions.append(getattr(self.model, k).like(f"{v}%"))
        return self

    def endLike(self, **kwargs):
        '''
        await User.query().like(name="Tom").all()
        SELECT * FROM user WHERE name LIKE '%Tom';
        '''
        for k, v in kwargs.items():
            if v:
                self._conditions.append(getattr(self.model, k).like(f"%{v}"))
        return self

    def greater_equal(self, **kwargs):
        '''
        await User.query().greater_equal(age=18).all()
        SELECT * FROM user WHERE age >= 18;
        '''
        for k, v in kwargs.items():
            self._conditions.append(getattr(self.model, k) >= v)
        return self

    def greater(self, **kwargs):
        '''
        await User.query().greater(age=18).all()
        SELECT * FROM user WHERE age > 18;
        '''
        for k, v in kwargs.items():
            self._conditions.append(getattr(self.model, k) > v)
        return self

    def less_equal(self, **kwargs):
        for k, v in kwargs.items():
            self._conditions.append(getattr(self.model, k) <= v)
        return self

    def less(self, **kwargs):
        '''
        await User.query().less(age=30).all()
        SELECT * FROM user WHERE age < 30;
        '''
        for k, v in kwargs.items():
            self._conditions.append(getattr(self.model, k) < v)
        return self

    def isin(self, **kwargs: dict[str, Iterable[Any]]):
        '''
        await User.query().isin(id=[1,2,3]).all()
        SELECT * FROM user WHERE id IN (1,2,3);
        '''
        for k, v in kwargs.items():
            self._conditions.append(getattr(self.model, k).in_(v))
        return self

    def notin(self, **kwargs: dict[str, Iterable[Any]]):
        '''
        await User.query().notin(id=[1,2]).all()
        SELECT * FROM user WHERE id NOT IN (1,2);
        '''
        for k, v in kwargs.items():
            self._conditions.append(getattr(self.model, k).notin_(v))
        return self

    def is_null(self, *columns: str):
        '''
        await User.query().is_null("name").all()
        SELECT * FROM user WHERE name IS NULL;
        '''
        for c in columns:
            self._conditions.append(getattr(self.model, c).is_(None))
        return self

    def is_not_null(self, *columns: str):
        '''
        await User.query().is_not_null("name").all()
        SELECT * FROM user WHERE name IS NOT NULL;
        '''
        for c in columns:
            self._conditions.append(getattr(self.model, c).isnot(None))
        return self

    # group / distinct / order / limit
    def group_by(self, *columns: str, with_count=False):
        '''
        await User.query().select("status").group_by("status").all()
        SELECT status, COUNT(*) AS count FROM user GROUP BY status;
        '''
        self._group_by = [getattr(self.model, c) for c in columns]
        self._with_count = with_count
        return self

    def distinct(self, *columns: str):
        '''
        rows = await User.query().select("name", "age").distinct().all()
        SELECT DISTINCT name, age FROM user;

        # PostgreSQL DISTINCT ON
        rows = await User.query().select("name", "age").distinct("name").order_by(User.name, User.age.desc()).all()
        SELECT DISTINCT ON (name) name, age FROM user ORDER BY name, age DESC;
        '''
        if columns:
            self._distinct_on = [getattr(self.model, c) for c in columns]
        else:
            self._distinct = True
        return self

    def order_by(self, *clauses):
        '''
        await User.query().order_by(User.age.desc()).all()
        SELECT * FROM user ORDER BY age DESC;
        '''
        self._order_by.extend(clauses)
        return self

    def order_by_key(self, model, sort: str):
        '''
        await User.query().order_by_key(User, "-age").all()
        SELECT * FROM user ORDER BY age DESC;
        '''
        order_type = sort.startswith("-")
        key = sort.lstrip("+-")
        col = model.__sortable__.get(key.strip())
        expr = col.desc() if order_type else col.asc()
        self._order_by.append(expr)
        return self

    def limit(self, limit: int):
        self._limit = limit
        return self

    def offset(self, offset: int):
        self._offset = offset
        return self

    def join(self, model, onclause, isouter=False):
        '''
        await User.query().join(Order, User.id == Order.user_id).all()\n
        SELECT user.* FROM user JOIN order ON user.id = order.user_id;

        await User.query().join(Order, User.id == Order.user_id, isouter=True).all()\n
        SELECT user.* FROM user LEFT OUTER JOIN order ON user.id = order.user_id;
        '''
        self._joins.append((model, onclause, isouter))
        return self

    def or_(self, *condition_dicts: dict):
        """
        跨字段的 OR 条件\n
        用法: await User.query().or_({"name": "Tom"}, {"age": 18}).all()\n
        SQL: SELECT * FROM user WHERE name = 'Tom' OR age = 18;
        """
        or_clauses = []
        for cond in condition_dicts:
            for k, v in cond.items():
                or_clauses.append(getattr(self.model, k) == v)
        if or_clauses:
            self._conditions.append(or_(*or_clauses))
        return self

    def where_raw(self, clause, **params):
        """
        传入原生 SQL 片段或 SQLAlchemy 表达式 (用于应对 ORM 无法覆盖的复杂场景)

        用法:
        1. await User.query().where_raw("JSON_EXTRACT(info, '$.vip') = true").all()
        2. await User.query().where_raw(User.age > 18).all()
        """
        if isinstance(clause, str):
            self._conditions.append(text(clause).bindparams(**params))
        else:
            self._conditions.append(clause)
        return self

    def where_exists(self, subquery):
        '''
        subq = Order.query().equal(user_id=User.id)._build_select()\n
        await User.query().where_exists(subq).all()\n
        SELECT * FROM user WHERE EXISTS (SELECT id FROM order WHERE order.user_id = user.id);
        '''
        self._conditions.append(exists(subquery))
        return self

    def where_not_exists(self, subquery):
        self._conditions.append(not_(exists(subquery)))
        return self

    def having_count(self, column: str = "*", op: str = ">", value: Any = 0):
        """
        HAVING COUNT 快捷方法 (无需导入 func)
        用法: await User.query().group_by("status").having_count(">", 5).all()
        SQL: ... HAVING COUNT(*) > 5
        """
        if column == "*":
            col_expr = func.count(text('*'))  # 显式使用 count(*)
        elif column == "1":
            col_expr = func.count(1)          # 显式使用 count(1)
        else:
            col_expr = func.count(getattr(self.model, column))  # count(column)
        self._having.append(self._build_agg_clause(col_expr, op, value))
        return self

    def having_sum(self, column: str, op: str, value: Any):
        """HAVING SUM 快捷方法"""
        self._having.append(self._build_agg_clause(func.sum(getattr(self.model, column)), op, value))
        return self

    def having_avg(self, column: str, op: str, value: Any):
        """HAVING AVG 快捷方法"""
        self._having.append(self._build_agg_clause(func.avg(getattr(self.model, column)), op, value))
        return self

    def having_max(self, column: str, op: str, value: Any):
        """HAVING MAX 快捷方法"""
        self._having.append(self._build_agg_clause(func.max(getattr(self.model, column)), op, value))
        return self

    def having_min(self, column: str, op: str, value: Any):
        """HAVING MIN 快捷方法"""
        self._having.append(self._build_agg_clause(func.min(getattr(self.model, column)), op, value))
        return self

    def having_raw(self, *clauses):
        """
        处理极其复杂的 HAVING 表达式 (保留原生能力)
        用法: await User.query().group_by("status").having_expr(func.sum(User.a) > func.sum(User.b)).all()
        """
        self._having.extend(clauses)
        return self

    def _build_agg_clause(self, agg_func, op: str, value):
        """内部辅助方法：构建聚合比较表达式"""
        op_map = {
            ">": agg_func > value, ">=": agg_func >= value,
            "<": agg_func < value, "<=": agg_func <= value,
            "=": agg_func == value, "!=": agg_func != value,
            "==": agg_func == value, "<>": agg_func != value,
            "in": agg_func.in_(value), "not in": agg_func.notin_(value),
            "between": agg_func.between(value[0], value[1])
        }
        if op not in op_map:
            raise ValueError(f"不支持的比较符: {op}，请使用 >, >=, <, <=, =, !=, in, not in, between")
        if op == "between":
            if not isinstance(value, (list, tuple)) or len(value) != 2:
                raise ValueError("between 的 value 必须是包含两个元素的列表或元组，如 (10, 20)")
        return op_map[op]

    def for_update(self, nowait: bool = False, skip_locked: bool = False):
        """
        添加 FOR UPDATE 锁 (防止并发修改)\n
        :param nowait: 如果获取不到锁是否立即报错 (PostgreSQL/MySQL 8.0+)
        :param skip_locked: 是否跳过被锁定的行

        用法: user = await User.query().equal(id=1).for_update().first()\n
        SQL: SELECT * FROM user WHERE id = 1 FOR UPDATE;
        """
        self._for_update = True
        self._for_update_opts = {'nowait': nowait, 'skip_locked': skip_locked}
        return self

    # build select
    def _build_select(self):
        if self._select_columns:
            columns = list(self._select_columns)
        else:
            columns = [self.model]

        if self._with_count:
            columns.append(func.count(text("*")).label("count"))

        stmt = select(*columns)

        if self._group_by and self._distinct:
            raise ValueError("distinct 和 group_by 不建议同时使用")

        if self._conditions:
            stmt = stmt.where(and_(*self._conditions))

        if self._group_by:
            stmt = stmt.group_by(*self._group_by)

        if self._having:
            stmt = stmt.having(*self._having)

        if self._distinct_on:
            stmt = stmt.distinct(*self._distinct_on)
        elif self._distinct:
            stmt = stmt.distinct()

        if self._order_by:
            stmt = stmt.order_by(*self._order_by)

        if self._limit is not None:
            stmt = stmt.limit(self._limit)
        if self._offset is not None:
            stmt = stmt.offset(self._offset)

        if self._joins:
            for model, onclause, isouter in self._joins:
                if isouter:
                    stmt = stmt.outerjoin(model, onclause)
                else:
                    stmt = stmt.join(model, onclause)

        if self._for_update and self._for_update_opts:
            stmt = stmt.with_for_update(**self._for_update_opts)

        return stmt

    # 执行（async）
    async def all(self):
        async with DBExecutor.session_scope() as session:
            stmt = self._build_select()
            result = await session.execute(stmt)
            return result.scalars().all() if self._select_columns is None else result.all()

    async def first(self):
        async with DBExecutor.session_scope() as session:
            stmt = self._build_select()
            result = await session.execute(stmt)
            row = result.first()
            return row[0] if row else None

    async def one(self):
        async with DBExecutor.session_scope() as session:
            stmt = self._build_select()
            result = await session.execute(stmt)
            return result.scalar_one()

    async def count(self) -> int:
        base_stmt = select(self.model)
        if self._conditions:
            base_stmt = base_stmt.where(*self._conditions)
        if self._group_by:
            base_stmt = base_stmt.group_by(*self._group_by)
        stmt = select(func.count()).select_from(base_stmt.subquery())
        async with DBExecutor.session_scope() as session:
            result = await session.execute(stmt)
            return result.scalar_one()

    async def delete(self):
        async def _write():
            async with DBExecutor.session_scope() as session:
                stmt = delete(self.model)
                if self._conditions:
                    stmt = stmt.where(and_(*self._conditions))
                result = await session.execute(stmt)
                return result.rowcount
        return await _execute_in_queue(_write)

    async def update(self, **kwargs):
        """
        按照多个where条件更新数据\n
        用法: await User.query().equal(status=0).update(status=1) \n
        生成SQL: UPDATE user SET status=1 WHERE status=0;
        """
        async def _write():
            async with DBExecutor.session_scope() as session:
                stmt = sa_update(self.model).values(**kwargs)
                if self._conditions:
                    stmt = stmt.where(and_(*self._conditions))
                result = await session.execute(stmt)
                return result.rowcount
        return await _execute_in_queue(_write)

    async def sum(self, column: str) -> float:
        """求和"""
        async with DBExecutor.session_scope() as session:
            stmt = select(func.sum(getattr(self.model, column)))
            if self._conditions: stmt = stmt.where(and_(*self._conditions))
            result = await session.execute(stmt)
            return result.scalar() or 0.0

    async def avg(self, column: str) -> float:
        """平均值"""
        async with DBExecutor.session_scope() as session:
            stmt = select(func.avg(getattr(self.model, column)))
            if self._conditions: stmt = stmt.where(and_(*self._conditions))
            result = await session.execute(stmt)
            return float(result.scalar() or 0.0)

    async def max(self, column: str) -> Any:
        """最大值"""
        async with DBExecutor.session_scope() as session:
            stmt = select(func.max(getattr(self.model, column)))
            if self._conditions: stmt = stmt.where(and_(*self._conditions))
            result = await session.execute(stmt)
            return result.scalar()

    async def min(self, column: str) -> Any:
        """最小值"""
        async with DBExecutor.session_scope() as session:
            stmt = select(func.min(getattr(self.model, column)))
            if self._conditions: stmt = stmt.where(and_(*self._conditions))
            result = await session.execute(stmt)
            return result.scalar()


class CRUDBase:
    @classmethod
    @deprecated("不推荐使用, 无法保证并发安全")
    async def create2return(cls, **kwargs):
        async with DBExecutor.session_scope() as session:
            instance = cls(**kwargs)
            session.add(instance)
            await session.flush()
            return instance

    @classmethod
    async def create(cls, **kwargs):
        '''
        user = await User.create(name="Tom", age=18)
        INSERT INTO user (name, age) VALUES ('Tom', 18);
        '''
        async def _write():
            async with DBExecutor.session_scope() as session:
                instance = cls(**kwargs)
                session.add(instance)
                await session.flush()
                return instance
        return await _execute_in_queue(_write)

    @classmethod
    async def bulk_create(cls, items: list[dict]):
        """
        批量插入数据 (性能远高于循环调用 create)\n
        用法: users = [{"name": "Tom", "age": 18}, {"name": "Jerry", "age": 20}]\n
        await User.bulk_create(users)
        """
        if not items:
            return []

        async def _write():
            async with DBExecutor.session_scope() as session:
                instances = [cls(**item) for item in items]
                session.add_all(instances)
                await session.flush()
                return instances
        return await _execute_in_queue(_write)

    @classmethod
    async def get(cls, value):
        """
        user = await User.get(1)
        SELECT * FROM user WHERE id = 1;
        """
        async with DBExecutor.session_scope() as session:
            return await session.get(cls, value)

    @classmethod
    async def get_one(cls, value):
        """
        If not existed, raise NoResultFound
        user = await User.get_one("cat001")
        """
        async with DBExecutor.session_scope() as session:
            return await session.get_one(cls, value)

    @classmethod
    def query(cls) -> BaseQueryBuilder:
        """
        users = await User.query().equal(name="Documents", is_delete=0).all()
        """
        return BaseQueryBuilder(cls)

    @classmethod
    @deprecated("不推荐使用, 无法保证并发安全")
    async def update2return(cls, pk, **kwargs):
        """
        await User.update(user_id, name="New Name", is_backup=1)
        """
        async with DBExecutor.session_scope() as session:
            instance = await session.get(cls, pk)
            if not instance:
                return None
            for key, value in kwargs.items():
                setattr(instance, key, value)
            await session.flush()
            return instance

    @classmethod
    async def update(cls, pk, **kwargs):
        """
        await User.update(1, name="Jerry", age=20)
        UPDATE user SET name='Jerry', age=20 WHERE id=1;
        """
        async def _write():
            async with DBExecutor.session_scope() as session:
                instance = await session.get(cls, pk)
                if not instance:
                    return None
                for key, value in kwargs.items():
                    setattr(instance, key, value)
                await session.flush()
                return instance
        return await _execute_in_queue(_write)

    @classmethod
    async def execute_sql(cls, sql: str, params: dict = None, fetch: str = "all"):
        """
        执行自定义原生 SQL (适用于 INSERT/UPDATE/DELETE 或复杂查询)\n
        执行 SELECT：根据 fetch 参数决定：fetch="all" 返回元组列表（如 [('Tom', 18), ('Jerry', 20)]）；fetch="one" 返回单个元组；fetch="scalar" 返回单个值（如 count(*) 的结果）\n
        执行 INSERT / UPDATE / DELETE：返回 result.rowcount（受影响的行数，整数类型）\n
        用法: rows = await User.execute_sql("DELETE FROM user WHERE age < :age", {"age": 18}, fetch="none")
        """
        async def _execute_sql(sql: str, params: dict = None, fetch: str = "all"):
            async with DBExecutor.session_scope() as session:
                result = await session.execute(text(sql), params or {})
                # 判断是否返回结果集 (SELECT 或带有 RETURNING 的 DML)
                if result.returns_rows:
                    if fetch == "one":
                        return result.fetchone()
                    elif fetch == "scalar":
                        return result.scalar()
                    else:
                        return result.fetchall()
                else:
                    # 对于普通的 INSERT/UPDATE/DELETE，返回受影响的行数
                    return result.rowcount
        sql_upper = sql.upper()
        if sql_upper.startswith('INSERT') or sql_upper.startswith('UPDATE') or sql_upper.startswith('DELETE'):
            async def _write():
                return await _execute_sql(sql, params, fetch)
            return await _execute_in_queue(_write)
        else:
            return await _execute_sql(sql, params, fetch)

    @classmethod
    async def raw_query(cls, sql: str, params: dict = None, as_dict: bool = False):
        """
        执行自定义 SELECT SQL。\n
        场景 A：查询所有字段，获取 ORM 对象列表 (必须 SELECT *) : 返回: [<User object at 0x...>, <User object at 0x...>]\n
        场景 B：只查询几个字段，获取字典列表 (使用 as_dict=True) : 返回: [{'id': 1, 'name': 'Tom'}, {'id': 2, 'name': 'Jerry'}]\n
        :param as_dict: 如果为 True，返回字典列表（适用于只查询部分字段的情况）；
                        如果为 False，返回 ORM 对象列表（要求 SQL 必须 SELECT 所有字段）。
        """
        async with DBExecutor.session_scope() as session:
            if as_dict:
                result = await session.execute(text(sql), params or {})
                return result.mappings().all()
            else:
                stmt = select(cls).from_statement(text(sql))
                result = await session.execute(stmt, params or {})
                return result.scalars().all()


class Group(Base, CRUDBase):
    __tablename__ = 'group'

    id = Column(String(16), primary_key=True)
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class User(Base, CRUDBase):
    __tablename__ = 'user'

    id = Column(String(16), primary_key=True)
    nickname = Column(String(16), nullable=False)
    password = Column(String(32), nullable=False)
    group_id = Column(String(16), ForeignKey('group.id'), nullable=False)
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class FileExplorer(Base, CRUDBase):
    __tablename__ = 'file_explorer'

    id = Column(String(16), primary_key=True)
    parent_id = Column(String(16), ForeignKey('file_explorer.id', ondelete='CASCADE'), nullable=True, index=True)
    name = Column(String(64), nullable=False)
    format = Column(String(16), nullable=True)
    size = Column(BigInteger, nullable=True)
    status = Column(Integer, default=0)  # -1:Deleted, 0:Normal, 99:BackedUp
    username = Column(String(16), nullable=False)
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    parent = relationship('FileExplorer', remote_side=[id])

    __sortable__ = {'id': id, 'size': size, 'update_time': update_time, 'name': name}

    async def full_path(self):
        paths = []
        current_node = self
        while current_node:
            paths.append(current_node.name)
            if current_node.parent_id:
                current_node = await FileExplorer.get_one(current_node.parent_id)
            else:
                current_node = None
        return '/'.join(paths[::-1])

    async def full_id(self):
        paths = []
        current_node = self
        while current_node:
            paths.append(current_node.id)
            if current_node.parent_id:
                current_node = await FileExplorer.get_one(current_node.parent_id)
            else:
                current_node = None
        return '/'.join(paths[::-1])


class Shares(Base, CRUDBase):
    __tablename__ = 'shares'

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_id = Column(String(16), nullable=False)
    name = Column(String(64), nullable=False)
    path = Column(String(256), nullable=False)
    format = Column(String(16), nullable=True)
    times = Column(Integer, default=0)
    username = Column(String(16), nullable=False)
    total_times = Column(Integer, default=1)
    create_time = Column(DateTime, default=datetime.now)


class Servers(Base, CRUDBase):
    __tablename__ = 'servers'

    id = Column(String(16), primary_key=True)
    host = Column(String(16), nullable=False)
    port = Column(Integer, default=22)
    user = Column(String(16), nullable=False)
    pwd = Column(String(36), nullable=False)
    system = Column(String(64), nullable=False)
    cpu = Column(Integer, default=1)
    mem = Column(Integer, default=0.1)
    disk = Column(String(8), nullable=False)
    username = Column(String(16), nullable=False)
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class Musics(Base, CRUDBase):
    __tablename__ = 'music'

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_id = Column(String(16), nullable=False)
    name = Column(String(64), nullable=False)
    singer = Column(String(16), nullable=False)
    duration = Column(String(16), nullable=False)
    username = Column(String(16), nullable=False)
    times = Column(Integer, default=1)
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    __sortable__ = {'duration': duration, 'create_time': create_time, 'update_time': update_time, 'times': times, 'name': name}


class Games(Base, CRUDBase):
    __tablename__ = 'games'

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(8), nullable=False)
    username = Column(String(16), nullable=False)
    score = Column(Integer, default=0)
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class Shortcuts(Base, CRUDBase):
    __tablename__ = 'shortcuts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_id = Column(String(16), nullable=False)
    name = Column(String(64), nullable=False)
    format = Column(String(16), nullable=False)
    username = Column(String(16), nullable=False)
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class Karaoke(Base, CRUDBase):
    __tablename__ = 'karaoke'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False)
    status = Column(Integer, default=0)  # 0 - Cannot sing, 1 - Can sing
    times = Column(Integer, default=0)
    is_sing = Column(Integer, default=0)  # 0 - Never sung, 1 - Clicked but not sung, 2 - Sung, -1 - Singing now
    is_top = Column(Integer, default=0)  # 0 - Not pinned, 1 - Pinned
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class ChatRoom(Base, CRUDBase):
    __tablename__ = 'chat_room'

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(8), nullable=False)
    mode = Column(Integer, default=0)  # 0 - Voice chat, 1 - Video chat, 2 - File transfer
    start_time = Column(Integer, default=0)
    end_time = Column(Integer, default=0)
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class Health(Base, CRUDBase):
    __tablename__ = 'health_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    mode = Column(Integer, default=1)  # 0 - Height, 1 - Weight, 2 - Heart rate, 3 - Blood pressure (systolic), 4 - Blood sugar, 5 - Blood oxygen, 333 - Diastolic pressure
    value = Column(BigInteger, nullable=False)
    username = Column(String(16), nullable=False)
    create_time = Column(DateTime, default=datetime.now)


class MigrateSql(Base, CRUDBase):
    __tablename__ = "migrate_sql"

    id = Column(Integer, primary_key=True)
    sql = Column(String(128), nullable=False)
    is_run = Column(Integer, default=0)


async def execute_sql(sql):
    session = await Database.get_session()
    try:
        await session.execute(text(sql))
        await session.commit()
    except:
        await session.rollback()
        raise
    finally:
        await Database.dispose()


async def init_data():
    migrate_lines_file = os.path.join(BASE_PATH, 'migrate_sql.txt')
    if await asyncio.to_thread(os.path.exists, migrate_lines_file):
        async with aiofiles.open(migrate_lines_file, 'r', encoding='utf-8') as f:
            migrate_lines = await f.readlines()
        for line in migrate_lines:
            sql_list = line.split('-')
            if len(sql_list) == 2:
                has_sql = await MigrateSql.get(sql_list[0])
                if not has_sql:
                    await MigrateSql.create(id=sql_list[0], sql=sql_list[1])

        all_sql = await MigrateSql.query().all()
        for sql in all_sql:
            if sql.is_run == 0:
                try:
                    await execute_sql(sql.sql)
                except:
                    pass
                await MigrateSql.update(sql.id, is_run=1)
