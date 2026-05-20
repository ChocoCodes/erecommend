from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List 

from app.schemas import RecommendationPayload, RecommendationResult
from app.pipeline.semantic import generate_recommendations
from app.pipeline.preprocess import (
    compile_profile_text, 
    standardized_grade_percentage, 
    get_academic_rating, 
    get_annual_gross_income_rating, 
    apply_bonus
)

app = FastAPI(
    title="eRecommend: eSkolar Recommendation Engine back-end",
    description="Hybrid AI recommendation backend executing CHED regulatory weighting and semantic similarity analysis.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Replace later with deployed URL and localhost
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/health")
async def health():
    """ Check if the API is currently active. """
    return {
        "status": "healthy",
        "engine": "eRecommend active."
    }

@app.post("/api/v1/recommend")
async def recommend(payload: RecommendationPayload):
    """ 
    Accept a student profile and a list of available scholarships to 
    generate a recommendation on which scholarship suits the applicant.
    """
    try:
        student = payload.student
        scholarships = payload.scholarships
        # Normalize gwa and prepare profile block
        student.gwa = standardized_grade_percentage(student.gwa)
        profile_text = compile_profile_text(student)

        print("Student Profile parsed cleanly! Validation successful.")
        print(f"Parsed Name: {student.full_name}, GWA: {student.gwa}")
        print(f"Success! Successfully parsed {len(scholarships)} scholarships.")

        # Calculate CHED ranking
        academic_pts = get_academic_rating(student.gwa)
        income_pts = get_annual_gross_income_rating(student.annual_family_income)
        bonus_pts = apply_bonus(student.special_group)

        print(f"Academic: {academic_pts}, Income: {income_pts}, Bonus: {bonus_pts}")

        # Final Score
        regulatory_score = ((academic_pts * 0.70) + (income_pts * 0.30)) + bonus_pts
        print(f"Score: {regulatory_score}")

        results = generate_recommendations(
            regulatory_score=regulatory_score,
            student_profile=profile_text,
            scholarships=scholarships,
            student_annual_income=student.annual_family_income
        )

        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"eRecommend engine error: {str(e)}")