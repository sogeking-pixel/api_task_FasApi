from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class TokenBaseModel(BaseModel):
    access_token: str = Field(title="the string of token")
    expires_at: datetime
    created_at: datetime
    user_id: int
    model_config = ConfigDict(from_attributes=True)

class TokenResponse(TokenBaseModel):
    id: int

class TokenCreate(TokenBaseModel):
    pass

class TokenData(BaseModel):
    username: str | None = None
    
class TokenModel(BaseModel):
    access_token: str
    token_type: str