from pydantic import BaseModel, ConfigDict


class CounselorInfo(BaseModel):
    id: int
    name: str


class AliasResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    alias: str


class AliasRequest(BaseModel):
    telegram_user_id: str  # hashed telegram user id


class CounselorResponse(BaseModel):
    id: int
    telegram_user_id: int
    name: str
    bio: str


class ResolveGroupResponse(BaseModel):
    target_group_id: int
    display_name: str


class ResolveGroupRequest(BaseModel):
    group_id: int


class GroupLinkResponse(BaseModel):
    group_link: str | None = None


class GroupLinkRequest(BaseModel):
    telegram_user_id: str  # hashed user id
    counselor_id: int


class CreateGroupRequest(BaseModel):
    user_alias: str
    user_group_link: str
    user_group_id: int
    counselor_id: int
    counselor_group_id: int


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
