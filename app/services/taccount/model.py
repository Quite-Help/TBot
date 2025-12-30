from pydantic import BaseModel


class CreateSessionResponse(BaseModel):
    user_group_link: str
