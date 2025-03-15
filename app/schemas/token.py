from pydantic import BaseModel, Field
from datetime import datetime

class TokenModel(BaseModel):
    id: int
    access_token: str = Field(title="the string of token")
    token_type: str
    created_at: datetime
    expires_at: datetime
    user_id: int = Field(ge=0, le=100, title="the id of the user is greater or equal than zero" ,examples=[1,2])
    class Config:
        orm_mode = True

class TokenData(BaseModel):
    username: str | None = None