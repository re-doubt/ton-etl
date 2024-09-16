from typing import Set, Union
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from pytoniq_core import Address, ExternalAddress
from dataclasses import asdict
from loguru import logger
import json
from dataclasses import dataclass

@dataclass
class FakeRecord:
    value: any
    topic: str

def serialize_addr(addr: Union[Address, ExternalAddress, None]) -> str:
    if isinstance(addr, Address):
        return addr.to_str(is_user_friendly=False).upper()
    if isinstance(addr, ExternalAddress): # extrernal addresses are not supported
        return None
    return None
    
class DB():
    def __init__(self):
        self.pool = pool.SimpleConnectionPool(1, 3)
        if not self.pool:
            raise Exception("Unable to init connection")
        # Stores the number of rows with update to control commit frequency
        self.updated = 0
        self.conn = None
        
    """
    Acquires connection from the pool. After the end of the session caller has to release it
    """
    def acquire(self):
        assert self.conn is None, "Connection was not released"
        self.conn = self.pool.getconn()

    def release(self):
        assert self.conn is not None, "Unable to release connection, was not acquired"
        self.conn.commit()
        self.pool.putconn(self.conn)
        self.conn = None
        self.updated = 0

    """
    Returns message body by body hash
    """
    def get_message_body(self, body_hash) -> str:
        assert self.conn is not None
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("select body from message_contents mc  where hash = %s", (body_hash, ))
            res = cursor.fetchone()
            if not res:
                return None
            return res['body']
    
    """
    Returns jetton master
    """
    def get_wallet_master(self, jetton_wallet: Address) -> str:
        assert self.conn is not None
        assert type(jetton_wallet) == Address
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("select jetton from jetton_wallets jw where address = %s",
                           (serialize_addr(jetton_wallet), ))
            res = cursor.fetchone()
            if not res:
                return None
            return res['jetton']
        
    """
    Returns message body for the parent message
    """
    def get_parent_message_body(self, msg_hash) -> str:
        assert self.conn is not None
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                           select mc.body from trace_edges te
                            join messages m on m.tx_hash = te.left_tx and m.direction ='in'
                            join message_contents mc on mc.hash = m.body_hash 
                            where te.msg_hash = %s
                           """, (msg_hash, ))
            res = cursor.fetchone()
            if not res:
                return None
            return res['body']

    def get_nft_sale(self, address: str) -> dict:
        assert self.conn is not None
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
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
        
    def is_tx_successful(self, tx_hash: str) -> dict:
        assert self.conn is not None
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                select compute_exit_code, action_result_code from transactions where hash = %s
                """, 
                (tx_hash,),
            )
            res = cursor.fetchone()
            if not res:
                return None
            return res['compute_exit_code'] == 0 and res['action_result_code'] == 0

    def serialize(self, obj):
        table = obj.__tablename__
        assert self.conn is not None
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
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
            names.append('created')
            names.append('updated')
            placeholders.append('now()')
            placeholders.append('now()')
            cursor.execute(f"""
                insert into parsed.{table}({",".join(names)}) values ({",".join(placeholders)})
                on conflict do nothing
                            """, tuple(values))
            self.updated += 1

    def insert_message_comment(self, msg_hash, comment):
        assert self.conn is not None
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(f"""
                insert into parsed.message_comments(hash, comment)
                           values (%s, %s)
                on conflict do nothing
                            """, (msg_hash, comment))
            self.updated += 1

    def insert_nft_item(self, address, index, collection_address, owner_address, last_trans_lt, code_hash, data_hash):
        assert self.conn is not None
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(f"""
                insert into public.nft_items(address, index, collection_address, owner_address, 
                           last_transaction_lt, code_hash, data_hash, init)
                           values (%s, %s, %s, %s, %s, %s, %s, true)
                on conflict do nothing
                            """, (address.to_str(is_user_friendly=False).upper(), index,
                                  serialize_addr(collection_address),
                                  serialize_addr(owner_address), last_trans_lt,
                                    code_hash, data_hash))
            self.updated += 1

    def insert_core_price(self, asset, price, obj):
        assert self.conn is not None
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(f"""
                insert into prices.core(tx_hash, lt, asset, price, price_ts, created, updated)
                           values(%s, %s, %s, %s, %s, now(), now())
                on conflict (tx_hash) do update 
                           set tx_hash = EXCLUDED.tx_hash,
                           lt = EXCLUDED.lt,
                           asset = EXCLUDED.asset,
                           price = EXCLUDED.price,
                           price_ts = EXCLUDED.price_ts,
                           updated = now()
                            """, (obj.get('last_trans_hash'), obj.get('last_trans_lt'), asset,
                                  price, obj.get('timestamp')))
            self.updated += 1

    def get_core_price(self, asset: str, timestamp: int) -> float:
        assert self.conn is not None
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                select price from prices.core where asset = %s
                and price_ts < %s order by price_ts desc limit 1
                """, 
                (asset, timestamp),
            )
            res = cursor.fetchone()
            if not res:
                return None
            return float(res['price'])
        
    def get_uniq_nft_item_codes(self) -> Set[str]:
        assert self.conn is not None
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("select distinct code_hash as h from nft_items ni")
            return set(map(lambda x: x['h'], cursor.fetchall()))
        
    # Returns the latest account state
    def get_latest_account_state(self, address: Address):
        assert self.conn is not None
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                select * from latest_account_states where account = %s
                """, 
                (address.to_str(is_user_friendly=False).upper(), )
            )
            res = cursor.fetchone()
            return res
        
    # for debugging purposese
    def get_messages_for_processing(self, tx_hash):

        assert self.conn is not None
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                select * from messages where tx_hash = %s
                """, 
                (tx_hash,),
            )
            return list(map(lambda x: FakeRecord(value=json.dumps(dict(x)).encode('utf-8'), topic="ton.public.messages"),
                            cursor.fetchall()))
        
    # for debugging purposese
    def get_account_state_for_processing(self, address):

        assert self.conn is not None
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                select * from latest_account_states where account = %s
                """, 
                (address,),
            )
            return list(map(lambda x: FakeRecord(value=json.dumps(dict(x)).encode('utf-8'), topic="ton.public.latest_account_states"),
                            cursor.fetchall()))
        