from pydantic import BaseModel, Field
from datetime import datetime

class TokenBaseModel(BaseModel):
    access_token: str = Field(title="the string of token")
    expires_at: datetime
    created_at: datetime
    user_id: int
    class Config:
        orm_mode = True

class TokenResponse(TokenBaseModel):
    id: int

class TokenCreate(TokenBaseModel):
    pass

class TokenData(BaseModel):
    username: str | None = None
    
class TokenModel(BaseModel):
    access_token: str
    token_type: str