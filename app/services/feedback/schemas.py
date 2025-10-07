from pydantic import BaseModel
from typing import Literal


class UserData(BaseModel):
    developmentLevel: Literal["d1", "d2", "d3", "d4"]
    leadershipStyle: Literal["s1", "s2", "s3", "s4"]
    userQuery: str
