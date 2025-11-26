from typing import Optional
from pydantic import BaseModel


class CompilerOutputSchema(BaseModel):
    success: bool = False
    return_code: Optional[int] = None
    compilation_time_ms: Optional[int] = None
