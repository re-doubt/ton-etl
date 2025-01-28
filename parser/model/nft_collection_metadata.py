from dataclasses import dataclass


@dataclass
class NFTCollectionMetadata:
    __tablename__ = "nft_collection_metadata"
    __schema__ = "parsed"

    address: str
    update_time_onchain: int
    content: str
    metadata_status: int = 0
    name: str = None
    description: str = None
    image: str = None
    image_data: str = None
    sources: str = None
    tonapi_image_url: str = None
    update_time_metadata: int = None
