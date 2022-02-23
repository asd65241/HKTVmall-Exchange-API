from typing import Optional
from pydantic import BaseModel

class Query(BaseModel):
    username: str
    password: str
    merchant: str