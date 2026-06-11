import pymysql
from config import DB_CONFIG
import contextlib


def get_connection():
    """获取数据库连接"""
    return pymysql.connect(**DB_CONFIG)


def query(sql, params=None, fetchone=False, fetchall=False):
    """执行普通SQL查询
    - fetchone=True: 返回单行
    - fetchall=True: 返回全部行
    - 否则执行写操作并commit
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            if fetchone:
                result = cur.fetchone()
                return result
            if fetchall:
                result = cur.fetchall()
                return result
            conn.commit()
            return cur.lastrowid
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


@contextlib.contextmanager
def transaction():
    """事务上下文管理器
    在同一个连接中执行多条SQL，保持LAST_INSERT_ID有效
    用法:
        with transaction() as (conn, cur):
            cur.execute(sql1, params1)
            cur.execute(sql2, params2)
            # 返回 cur.lastrowid 可在上下文中使用
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            yield cur
            conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def insert_return_id(sql, params=None):
    """在同一连接中执行INSERT并返回LAST_INSERT_ID"""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            eid = cur.lastrowid
            conn.commit()
            return eid
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def callproc(proc_name, args=(), fetch_result=False):
    """调用存储过程
    - proc_name: 存储过程名称
    - args: 参数元组（IN参数）或列表
    - fetch_result: 是否返回结果集（用于返回结果集的存储过程）
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            if fetch_result:
                # 存储过程返回结果集
                cur.callproc(proc_name, args)
                result = cur.fetchall()
                conn.commit()
                return result
            else:
                # 存储过程有OUT参数
                cur.callproc(proc_name, args)
                conn.commit()
                # 获取最后一个OUT参数（MySQL存储过程OUT参数存储在 @_procname_n 变量中）
                cur.execute(f'SELECT @_{proc_name}_1')
                out_val = cur.fetchone()
                if out_val:
                    return out_val
                return None
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()