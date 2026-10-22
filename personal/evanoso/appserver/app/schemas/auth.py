# ==== LAYER 2: Identity & Access ====
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"