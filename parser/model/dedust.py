from pytoniq_core import Slice, Address

def read_dedust_asset(cell: Slice):
    kind = cell.load_uint(4)
    if kind == 0:
        return Address("EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM9c")
    else:
        wc = cell.load_uint(8)
        account_id = cell.load_bytes(32) # 256 bits
        return Address((wc, account_id))