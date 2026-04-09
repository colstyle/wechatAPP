# -*- coding: utf-8 -*-
"""
数据库连接
"""
import pymysql
from pymysql.cursors import DictCursor
from config import settings


class Database:
    """数据库连接管理"""

    _connection = None

    @classmethod
    def get_connection(cls):
        """获取数据库连接"""
        if cls._connection is None:
            cls._connection = pymysql.connect(
                host=settings.DB_HOST,
                port=settings.DB_PORT,
                user=settings.DB_USER,
                password=settings.DB_PASSWORD,
                database=settings.DB_NAME,
                charset='utf8mb4',
                cursorclass=DictCursor,
                autocommit=False
            )
        return cls._connection

    @classmethod
    def close_connection(cls):
        """关闭数据库连接"""
        if cls._connection:
            cls._connection.close()
            cls._connection = None

    @classmethod
    def execute_query(cls, sql, params=None):
        """执行查询"""
        try:
            conn = cls.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(sql, params or ())
                return cursor.fetchall()
        except Exception as e:
            print(f"Database Query Error: {str(e)}")
            print(f"SQL: {sql}")
            print(f"Params: {params}")
            raise e

    @classmethod
    def execute_one(cls, sql, params=None):
        """执行查询，返回单条"""
        try:
            conn = cls.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(sql, params or ())
                return cursor.fetchone()
        except Exception as e:
            print(f"Database Execute One Error: {str(e)}")
            print(f"SQL: {sql}")
            print(f"Params: {params}")
            raise e

    @classmethod
    def execute_update(cls, sql, params=None):
        """执行更新/插入/删除"""
        try:
            conn = cls.get_connection()
            with conn.cursor() as cursor:
                result = cursor.execute(sql, params or ())
                conn.commit()
                return result
        except Exception as e:
            print(f"Database Update Error: {str(e)}")
            print(f"SQL: {sql}")
            print(f"Params: {params}")
            conn.rollback()
            raise e

    @classmethod
    def execute_insert(cls, sql, params=None):
        """执行插入，返回ID"""
        try:
            conn = cls.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(sql, params or ())
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"Database Insert Error: {str(e)}")
            print(f"SQL: {sql}")
            print(f"Params: {params}")
            conn.rollback()
            raise e

    @classmethod
    def execute_many(cls, sql, params_list):
        """批量执行"""
        conn = cls.get_connection()
        with conn.cursor() as cursor:
            result = cursor.executemany(sql, params_list)
            conn.commit()
            return result

    @classmethod
    def begin_transaction(cls):
        """开始事务"""
        conn = cls.get_connection()
        conn.begin()

    @classmethod
    def commit(cls):
        """提交事务"""
        conn = cls.get_connection()
        conn.commit()

    @classmethod
    def rollback(cls):
        """回滚事务"""
        conn = cls.get_connection()
        conn.rollback()


db = Database()
