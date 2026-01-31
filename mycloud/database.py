#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

import os
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, BigInteger
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import text
from datetime import datetime
from settings import DB_URL, DB_POOL_SIZE, BASE_PATH

Base = declarative_base()


class Database:
    engine = create_engine(DB_URL, echo=False, pool_size=DB_POOL_SIZE, max_overflow=DB_POOL_SIZE * 2, pool_timeout=30, pool_recycle=3600, pool_pre_ping=True, pool_use_lifo=True)
    session_factory = sessionmaker(bind=engine)

    @classmethod
    def get_session(cls):
        return cls.session_factory()

    # @classmethod
    # def close_session(cls):
    #     cls.session.remove()

    @classmethod
    def init_db(cls):
        Base.metadata.create_all(bind=cls.engine)


class CRUDBase:
    @classmethod
    def create(cls, **kwargs):
        with Database.get_session() as session:
            with session.begin():
                instance = cls(**kwargs)
                session.add(instance)
            session.refresh(instance)
            return instance

    @classmethod
    def get(cls, value):
        """
        user = User.get("cat001")
        """
        with Database.get_session() as session:
            return session.get(cls, value)

    @classmethod
    def get_one(cls, value):
        """
        If not existed, raise NoResultFound
        user = User.get_one("cat001")
        """
        with Database.get_session() as session:
            return session.get_one(cls, value)

    @classmethod
    def all(cls):
        """
        Query all datas.
        users = User.all()
        """
        with Database.get_session() as session:
            return session.query(cls)

    @classmethod
    def query(cls, **kwargs):
        """
        users = User.query(name="Documents", is_delete=0).all()
        """
        with Database.get_session() as session:
            return session.query(cls).filter_by(**kwargs)

    @classmethod
    def filter(cls, *filters, **kwargs):
        """
        users = User.filter(like(Catalog.name, "%Doc%"), is_delete=0).all()
        users = User.filter(or_(User.nickname == "John", User.nickname == "Jane")).all()
        """
        with Database.get_session() as session:
            query = session.query(cls)
            for filter_condition in filters:
                query = query.filter(filter_condition)
            for key, value in kwargs.items():
                query = query.filter(getattr(cls, key) == value)
            return query

    @classmethod
    def filter_condition(cls, equal_condition: dict = None, not_equal_condition: dict = None, like_condition: dict = None):
        """
        users = User.filter_condition(equal_condition={'status': 1, 'name': '222'}, not_equal_condition={'description': 'temp'})
        SELECT * FROM catuseralog WHERE status = 1 AND name = '222' AND description != 'temp';
        """
        with Database.get_session() as session:
            query = session.query(cls)
            if equal_condition:
                for column, value in equal_condition.items():
                    query = query.filter(getattr(cls, column) == value)
            if like_condition:
                for column, value in like_condition.items():
                    query = query.filter(getattr(cls, column).like(f'%{value}%'))
            if not_equal_condition:
                for column, value in not_equal_condition.items():
                    query = query.filter(getattr(cls, column) != value)
            return query

    @classmethod
    def update(cls, instance, **kwargs):
        """
        updated_user = User.update(user, name="New Name", is_backup=1)
        """
        with Database.get_session() as session:
            with session.begin():
                if instance in session:
                    current_instance = instance
                else:
                    current_instance = session.merge(instance, load=False)
                for key, value in kwargs.items():
                    setattr(current_instance, key, value)
            session.refresh(current_instance)
            return current_instance

    @classmethod
    def batch_update(cls, filter_criteria, update_values):
        """
        User.bulk_update(filter_criteria={"role": "admin"}, update_values={"is_active": True})
        """
        with Database.get_session() as session:
            with session.begin():
                session.query(cls).filter_by(**filter_criteria).update(update_values)

    @classmethod
    def delete(cls, instance):
        """
        User.delete(user)
        """
        with Database.get_session() as session:
            with session.begin():
                current_instance = session.get(cls, instance.id)
                session.delete(current_instance)


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

    @property
    def full_path(self):
        paths = []
        current_node = self
        while current_node:
            paths.append(current_node.name)
            current_node = current_node.get(current_node.parent_id)
        return '/'.join(paths[::-1])

    @property
    def full_id(self):
        paths = []
        current_node = self
        while current_node:
            paths.append(current_node.id)
            current_node = current_node.get(current_node.parent_id)
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


def execute_sql(sql):
    session = Database.get_session()
    try:
        session.execute(text(sql))
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        Database.close_session()


def init_data():
    migrate_lines_file = os.path.join(BASE_PATH, 'migrate_sql.txt')
    if os.path.exists(migrate_lines_file):
        with open(migrate_lines_file, 'r', encoding='utf-8') as f:
            migrate_lines = f.readlines()
        for line in migrate_lines:
            sql_list = line.split('-')
            if len(sql_list) == 2:
                has_sql = MigrateSql.get(sql_list[0])
                if not has_sql:
                    MigrateSql.create(id=sql_list[0], sql=sql_list[1])

        all_sql = MigrateSql.all()
        for sql in all_sql:
            if sql.is_run == 0:
                try:
                    execute_sql(sql.sql)
                except:
                    pass
                MigrateSql.update(sql, is_run=1)
