from pydantic import BaseModel, Field
from datetime import datetime

class TokenBaseModel(BaseModel):
    access_token: str = Field(title="the string of token")
    token_type: str
    expires_at: datetime
    user_id: int
    class Config:
        orm_mode = True

class TokenResponse(TokenBaseModel):
    id: int
    created_at: datetime

class TokenCreate(TokenBaseModel):
    pass

class TokenData(BaseModel):
    username: str | None = None