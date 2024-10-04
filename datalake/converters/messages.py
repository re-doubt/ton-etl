import base64
import psycopg2
from functools import lru_cache
from loguru import logger
from pytoniq_core import Cell
from psycopg2.extras import RealDictCursor
from converters.converter import Converter


class MessageConverter(Converter):
    def __init__(self):
        super().__init__("schemas/messages.avsc")
        # Use simple connection created on startup. If it fails, we will fail recover after restart
        self.conn = psycopg2.connect()


    # Using lru cache to minimize number of calls to the database for frequently user payloads
    @lru_cache(maxsize=1000)
    def get_body_and_comment(self, body_hash):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(f"SELECT body FROM message_contents WHERE hash = '{body_hash}'")
            res = cursor.fetchone()
            if not res:
                logger.warning("Unable to find message body for hash {body_hash}")
                return None, None
            body_boc = base64.b64decode(res['body'])
            comment = None
            cell = Cell.one_from_boc(res['body']).begin_parse()
            try:
                comment = cell.load_snake_string().replace('\x00', '')
            except Exception as e:
                pass
            return body_boc, comment

    def convert(self, obj):
        body_hash = obj['body_hash']
        # logger.info(f"Converting message {body_hash}")
        obj['body_boc'], obj['comment'] = self.get_body_and_comment(body_hash)
        if obj['created_at'] is None:
            # ExtIn has a lack of created_lt, according to spec. We will use created_at from transaction
            with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(f"select  now from transactions where hash = %s and lt = %s", (obj['tx_hash'], obj['tx_lt']))
                res = cursor.fetchone()
                assert res is not None, f"Unable to find tx for {obj}"
                obj['created_at'] = res['now']
        return super().convert(obj)