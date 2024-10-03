import psycopg2
from loguru import logger
from pytoniq_core import Cell
from psycopg2.extras import RealDictCursor
from converters.converter import Converter


class MessageConverter(Converter):
    def __init__(self):
        super().__init__("schemas/messages.avsc")
        # Use simple connection created on startup. If it fails, we will fail recover after restart
        self.conn = psycopg2.connect()

    def convert(self, obj):
        body_hash = obj['body_hash']
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(f"SELECT body FROM message_contents WHERE hash = '{body_hash}'")
            res = cursor.fetchone()
            if not res:
                logger.warning("Unable to find message body for hash {body_hash}")
                return obj
            obj['body_boc'] = res['body']
            cell = Cell.one_from_boc(res['body']).begin_parse()
            try:
                obj['comment'] = cell.load_snake_string().replace('\x00', '')
            except Exception as e:
                pass
        return obj