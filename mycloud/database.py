#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

import os
import asyncio
import aiofiles
from typing import Iterable, Any
from contextlib import asynccontextmanager
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, BigInteger
from sqlalchemy import func, select, delete, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import and_
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

    # 查询指定的字段
    def select(self, *columns: str):
        self._select_columns = [getattr(self.model, c) for c in columns]
        return self

    # where 条件
    def equal(self, **kwargs):
        for k, v in kwargs.items():
            self._conditions.append(getattr(self.model, k) == v)
        return self

    def not_equal(self, **kwargs):
        for k, v in kwargs.items():
            self._conditions.append(getattr(self.model, k) != v)
        return self

    def like(self, **kwargs):
        for k, v in kwargs.items():
            if v:
                self._conditions.append(getattr(self.model, k).like(f"%{v}%"))
        return self

    def greater_equal(self, **kwargs):
        for k, v in kwargs.items():
            self._conditions.append(getattr(self.model, k) >= v)
        return self

    def greater(self, **kwargs):
        for k, v in kwargs.items():
            self._conditions.append(getattr(self.model, k) > v)
        return self

    def less_equal(self, **kwargs):
        for k, v in kwargs.items():
            self._conditions.append(getattr(self.model, k) <= v)
        return self

    def less(self, **kwargs):
        for k, v in kwargs.items():
            self._conditions.append(getattr(self.model, k) < v)
        return self

    def isin(self, **kwargs: dict[str, Iterable[Any]]):
        for k, v in kwargs.items():
            self._conditions.append(getattr(self.model, k).in_(v))
        return self

    def notin(self, **kwargs: dict[str, Iterable[Any]]):
        for k, v in kwargs.items():
            self._conditions.append(getattr(self.model, k).notin_(v))
        return self

    def is_null(self, *columns: str):
        for c in columns:
            self._conditions.append(getattr(self.model, c).is_(None))
        return self

    def is_not_null(self, *columns: str):
        for c in columns:
            self._conditions.append(getattr(self.model, c).isnot(None))
        return self

    # group / order / limit
    def group_by(self, *columns: str, with_count=True):
        self._group_by = [getattr(self.model, c) for c in columns]
        self._with_count = with_count
        return self

    def order_by(self, *clauses):
        self._order_by.extend(clauses)
        return self

    def order_by_key(self, model, sort: str):
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

    # build select
    def _build_select(self):
        if self._select_columns:
            columns = list(self._select_columns)
        else:
            columns = [self.model]

        if self._with_count:
            columns.append(func.count("*").label("count"))

        stmt = select(*columns)

        if self._conditions:
            stmt = stmt.where(and_(*self._conditions))

        if self._group_by:
            stmt = stmt.group_by(*self._group_by)

        if self._order_by:
            stmt = stmt.order_by(*self._order_by)

        if self._limit is not None:
            stmt = stmt.limit(self._limit)
        if self._offset is not None:
            stmt = stmt.offset(self._offset)

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
        async with DBExecutor.session_scope() as session:
            stmt = delete(self.model)
            if self._conditions:
                stmt = stmt.where(and_(*self._conditions))
            result = await session.execute(stmt)
            return result.rowcount


class CRUDBase:
    @classmethod
    async def create2return(cls, **kwargs):
        async with DBExecutor.session_scope() as session:
            instance = cls(**kwargs)
            session.add(instance)
            await session.flush()
            return instance

    @classmethod
    async def create(cls, **kwargs):
        loop = asyncio.get_running_loop()
        future = loop.create_future()

        async def _write():
            async with DBExecutor.session_scope() as session:
                instance = cls(**kwargs)
                session.add(instance)
                await session.flush()
                return instance
        await writer_queue.put((_write, future))
        return await future

    @classmethod
    async def get(cls, value):
        """
        user = await User.get("cat001")
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
        rows = await User.query().select("id", "name").equal(is_delete=0).all()
        rows = await User.query().select("id", "name").equal(is_delete=0).group_by("id", "name", with_count=True).all()
        count = await User.query().equal(status=0).greater(id=10).delete()
        """
        return BaseQueryBuilder(cls)

    @classmethod
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
        await User.update(user_id, name="New Name", is_backup=1)
        """
        loop = asyncio.get_running_loop()
        future = loop.create_future()

        async def _write():
            async with DBExecutor.session_scope() as session:
                instance = await session.get(cls, pk)
                if not instance:
                    return None
                for key, value in kwargs.items():
                    setattr(instance, key, value)
                await session.flush()
                return instance
        await writer_queue.put((_write, future))
        return await future


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
    if os.path.exists(migrate_lines_file):
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
