from pydantic import BaseModel


class PaginationBaseModel(BaseModel):
    count: int
    next_link : str | None
    previous_link: str | None

    
    