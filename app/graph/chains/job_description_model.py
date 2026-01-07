from pydantic import BaseModel
from typing import List


class JobDescription(BaseModel):
    position: str | None
    seniority: str | None
    industry: str | None
    employment_type: str | None
    location: str | None
    hard_skills: List[str] | None
    soft_skills: List[str] | None
    tech_stack: List[str] | None
    must_haves: List[str] | None
    nice_to_haves: List[str] | None
    responsibilities: List[str] | None
    keywords_for_ats: List[str] | None
