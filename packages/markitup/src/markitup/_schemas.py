from ast import Tuple
from typing import Optional, List, Literal, Dict, Any, Tuple, override

from pydantic import BaseModel, Field


CHUNK_SIZE = 300
TIKTOKEN_ENCODER = 'gpt-4'


class StreamInfo(BaseModel):
    magic_type: Optional[str] = None
    category: Optional[str] = None


class Config(BaseModel):
    modalities: List[Literal["image", "audio"]] = Field(
        default_factory=lambda: ["image", "audio"]
    )
    chunk: bool = False
    chunk_size: int = CHUNK_SIZE
    # CHUNK_OVERLAP = 0 # Warning, the current pdf chunking localization depends on chunk_overlap == 0
    tiktoken_encoder: str = TIKTOKEN_ENCODER
    image_use_webp: bool = True  # TODO: support files contains images
    image_max_width_or_height: int = 768


class MarkdownChunk(BaseModel):
    chunk_modality: Literal["text", "image"]
    content: str  # The content of the chunk ONLY contains one type of modality

    # LOCATION INFO
    chunk_id: int  # The global chunk id of the chunk

    page_id: Optional[int] = None  # The 0-based page id of the chunk, currently exclusive for pdf

    bbox_id_list: Optional[List[int]] = Field(
        default_factory=list
    )  # The 0-based bounding box id of the chunk, currently exclusive for pdf

    bbox_list: Optional[List[Tuple[float, float, float, float]]] = Field(
        default_factory=list
    )  # The bounding box of the chunk, currently exclusive for pdf


class Chunk(BaseModel):
    chunk_modality: Literal["text", "image", "audio"]
    content: Dict[str, Any]  # The content of the chunk ONLY contains one type of modality

    # LOCATION INFO
    chunk_id: int  # The global chunk id of the chunk @rong: do we need a local chunk id here?

    page_id: Optional[int] = None  # The 0-based page id of the chunk, currently exclusive for pdf
    
    bbox_list: Optional[List[Tuple[float, float, float, float]]] = None  # The bounding box of the chunk, currently exclusive for pdf