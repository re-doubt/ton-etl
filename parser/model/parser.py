
#!/usr/bin/env python

from pytoniq_core import Address, Cell
from db import DB


TOPIC_MESSAGES = "ton.public.messages"
TOPIC_NFT_TRANSFERS = "ton.public.nft_transfers"

"""
Base class for parser
"""
class Parser:
    """
    Returns list of the topics this parser is able to handle data from
    """
    def topics(self):
        raise Exception("Not implemented")
    
    """
    Check is this object could be processed by the parser
    """
    def predicate(self, obj) -> bool:
        raise Exception("Not implemented")
    
    """
    Handles the object that passed predicate check
    """
    def handle_internal(self, obj, db: DB):
        raise Exception("Not implemented")
    
    def handle(self, obj, db: DB):
        if self.predicate(obj):
            # TODO handle errors?
            self.handle_internal(obj, db)
            return True
        return False
    
    """
    Helper method to convert uint values to int
    """
    @classmethod
    def opcode_signed(clz, opcode):
        return opcode if opcode < 0x80000000 else -1 * (0x100000000 - opcode)
    
    """
    Converts user friendly address to raw format
    """
    @classmethod
    def uf2raw(clz, addr):
        return  Address(addr).to_str(is_user_friendly=False).upper()
    
    """
    Returns non-null values or raises exception otherwise
    """
    @classmethod
    def require(clz, value, msg="Value is null"):
        if value is None:
            raise Exception(msg)
        return value
    
    """
    Extract message body from DB and return parsed cell
    """
    @classmethod
    def message_body(clz, obj, db: DB) -> Cell:
        return Cell.one_from_boc(Parser.require(db.get_message_body(obj.get('body_hash'))))