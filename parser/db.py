from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from pytoniq_core import Address
from dataclasses import asdict
from loguru import logger

class DB():
    def __init__(self):
        self.pool = pool.SimpleConnectionPool(1, 3)
        if not self.pool:
            raise Exception("Unable to init connection")

    """
    Returns message body by body hash
    """
    def get_message_body(self, body_hash) -> str:
        conn = self.pool.getconn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("select body from message_contents mc  where hash = %s", (body_hash, ))
                res = cursor.fetchone()
                if not res:
                    return None
                return res['body']

        finally:
            self.pool.putconn(conn)

    def get_account_code_hash(self, address: str) -> str:
        conn = self.pool.getconn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("select code_hash from latest_account_states where address = %s", (address,))
                res = cursor.fetchone()
                if not res:
                    return None
                return res['code_hash']

        finally:
            self.pool.putconn(conn)

    def get_nft_sale(self, address: str) -> dict:
        conn = self.pool.getconn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    select address, marketplace_address as marketplace, nft_owner_address as owner, 
                    full_price as price, false as is_auction, code_hash
                    from getgems_nft_sales where address = %s
                    union
                    select address, mp_addr as marketplace, nft_owner as owner, 
                    last_bid as price, true as is_auction, code_hash
                    from getgems_nft_auctions where address = %s
                    """, 
                    (address, address),
                )
                res = cursor.fetchone()
                return res

        finally:
            self.pool.putconn(conn)

    def serialize(self, obj):
        table = obj.__tablename__
        conn = self.pool.getconn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                names = []
                values = []
                placeholders = []
                for k, v in asdict(obj).items():
                    if k.startswith("_"):
                        continue
                    names.append(k)
                    if type(v) == Address:
                        v = v.to_str(is_user_friendly=False).upper()
                    values.append(v)
                    placeholders.append('%s')
                # TODO add support for upsert
                cursor.execute(f"""
                    insert into parsed.{table}({",".join(names)}) values ({",".join(placeholders)})
                    on conflict do nothing
                               """, tuple(values))
            conn.commit()
        finally:
            self.pool.putconn(conn)