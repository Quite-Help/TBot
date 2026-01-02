from pydantic import BaseModel, ConfigDict


class CounselorInfo(BaseModel):
    id: str
    name: str


class AliasResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    alias: str


class CounselorsResponse(BaseModel):
    counselors: list[CounselorInfo]


class CounselorResponse(BaseModel):
    id: str
    name: str
    bio: str


class ResolveGroupResponse(BaseModel):
    target_group_id: int
    display_name: str


class GroupLinkResponse(BaseModel):
    group_link: str | None = None
