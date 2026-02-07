from pydantic import BaseModel


class CreateSessionResponse(BaseModel):
    counselor_group_id: int
    user_group_id: int
    user_group_link: str
