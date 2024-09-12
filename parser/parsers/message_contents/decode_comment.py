from model.parser import Parser, TOPIC_MESSAGE_CONTENTS
from loguru import logger
from db import DB
from pytoniq_core import Cell, Address
from model.dexswap import DexSwapParsed
from parsers.message.swap_volume import estimate_volume


"""
ton-indexer doesn't have comment field in the messages table, so let's try to 
implement comments parsing on the parsing level

CREATE TABLE parsed.message_comments (
	hash bpchar(44) primary key, 
	comment varchar
);

"""
class CommentsDecoder(Parser):
    
    def topics(self):
        return [TOPIC_MESSAGE_CONTENTS]

    def predicate(self, obj) -> bool:
        return True
    
    def handle_internal(self, obj, db: DB):
        cell = Cell.one_from_boc(obj['body']).begin_parse()
        try:
            comment = cell.load_snake_string().replace('\x00', '')
        except Exception as e:
            # most probably the cell contains some other binary data
            # logger.error(f"Failed to parse comment: {e}")
            return
        db.insert_message_comment(obj['hash'], comment)
