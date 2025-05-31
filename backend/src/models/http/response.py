from pydantic import BaseModel
from typing import Optional, Literal

class StatusResponse(BaseModel):
	status: Literal['success', 'error', 'warning']
	message: Optional[str] = None