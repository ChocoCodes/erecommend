from pydantic import BaseModel
from typing import List, Optional

class ProfileItem(BaseModel):
    title: str 
    description: Optional[str] = None 
    issuer: Optional[str] = None 
    organization: Optional[str] = None 
    category: str 
    duration: Optional[str] = None

class StudentProfile(BaseModel):
    full_name: str 
    city: str 
    region: str 
    bio: str 
    gwa: float 
    highest_degree: str 
    date_of_birth: str
    annual_family_income: float 
    special_group: Optional[str] = None 
    profile_items: List[ProfileItem]

class Scholarship(BaseModel):
    id: int
    program_name: str 
    provider_name: str 
    status: str 
    grant_type: str 
    deadline: str 
    cutoff_grade: float 
    description: str 
    annual_family_income: Optional[float] = None 
    eligibility: str 
    tags: Optional[List[str]] = None

class RecommendationPayload(BaseModel):
    student: StudentProfile 
    scholarships: List[Scholarship]

class ScoreBreakdown(BaseModel):
    eligibility: float
    profile: float 
    academic: float
    income: float 
    bonus: float

class RecommendationResult(BaseModel):
    id: int 
    e_recommend: float 
    match: str 
    breakdown: ScoreBreakdown