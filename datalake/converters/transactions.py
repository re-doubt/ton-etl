import base64
import psycopg2
from functools import lru_cache
from loguru import logger
from pytoniq_core import Cell
from psycopg2.extras import RealDictCursor
from converters.converter import Converter


class TransactionsConverter(Converter):
    def __init__(self):
        super().__init__("schemas/transactions.avsc")


    def timestamp(self, obj):
        return obj['now']


    """
    code hash and balance added to transaction on the indexer level
    def convert(self, obj):
        if obj['end_status'] != 'nonexist' and obj['account_state_hash_after']:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(f"select * from account_states where hash = %s ", (obj['account_state_hash_after'],))
                res = cursor.fetchone()
                if res is None:
                    logger.warning(f"Unable to find state for {obj['account_state_hash_after']} for tx {obj['hash']}")
                else:
                    obj['account_state_code_hash_after'] = res['code_hash']
                    obj['account_state_balance_after'] = res['balance']
        return super().convert(obj)
    """