from mysql.connector import connect
from . import config as cfg

config = {
    'user': cfg.get(prefix='DATABASE', key='DB_USR'),
    'password': cfg.get(prefix='DATABASE', key='DB_PWD', encrypted=True),
    'host': cfg.get(prefix='DATABASE', key='DB_HOST'),
    'database': cfg.get(prefix='DATABASE', key='DB_NAME'),
    'raise_on_warnings': True
}


class Cursor:
    def __init__(self):
        self.conn = connect(**config)
        self.cursor = self.conn.cursor(buffered=True)

    def __iter__(self):
        for item in self.cursor:
            yield item

    def __enter__(self):
        # print('Database opened successfully')
        return self.cursor

    def __exit__(self, ext_type, exc_value, traceback):
        self.cursor.close()
        if isinstance(exc_value, Exception):
            self.conn.rollback()
        else:
            self.conn.commit()
        self.conn.close()
        # print('Database closed gracefully')
