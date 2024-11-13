from dataclasses import dataclass


@dataclass
class JettonMetadata:
    __tablename__ = "jetton_metadata"
    __schema__ = "parsed"

    address: str
    update_time_onchain: int
    mintable: bool
    admin_address: str
    jetton_content_onchain: str
    jetton_wallet_code_hash: str
    code_hash: str
    metadata_status: int = 0
    symbol: str = None
    name: str = None
    description: str = None
    image: str = None
    image_data: str = None
    decimals: int = None
    sources: str = None
    tonapi_image_url: str = None
    update_time_metadata: int = None
