from pydantic import BaseModel, Field 
from typing import List, Dict, Any, Optional 

class NetworkState(BaseModel): 
    messages: List[Dict[str, Any]] = Field(default_factory=list)

    # if None, the network stops
    next_agent_name: Optional[str] = None 

    result: Optional[str] = None 

    scratchpad: Dict[str, Any] = Field(default_factory=dict)