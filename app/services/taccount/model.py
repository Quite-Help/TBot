from pydantic import BaseModel


class CreateSessionResponse(BaseModel):
    counselor_group_id: str
    user_group_id: str
    user_group_link: str
