from typing import List, Optional, NamedTuple, Dict, Union
from dataclasses import dataclass
from enum import Enum

@dataclass
class AcidCosineResult:
    result_cosine: List[float]
    meta_data: Dict

@dataclass
class AcidBoolResult:
    result: bool
    meta_data: Dict

@dataclass
class AcidFloatResult:
    result: float 
    meta_data: Dict

class AcidTestType(Enum):
    BOOL = "bool"
    COSINE = "cosine"
    FLOAT = "float"

class FunctionInfo(NamedTuple):
    function_name: str
    bucket_name: Optional[str]
    filenames: List[str]
    return_type: Union[AcidBoolResult, AcidFloatResult, AcidCosineResult]
    name_sut: str

@dataclass
class CorrosiveTaskData:
    meta_data: Optional[Dict] = None
    t0: Optional[int] = None
    t1: Optional[int] = None
    result: Optional[bool] = None
    
    # Optional fields for cosine tasks
    buffer_1: Optional[List[float]] = None
    buffer_2: Optional[List[float]] = None

@dataclass
class CorrosiveSimilarity:
    embedder: str
    score_against: List[str]
    min_similarity: float
    max_distance: float

@dataclass
class CorrosiveTask:
    task_id: str 
    name: str
    func: FunctionInfo
    data: CorrosiveTaskData
    args: Optional[List[str]]
    similarity: Optional[CorrosiveSimilarity] = None
    run: Optional[int] = None
    succes: Optional[bool] = False
