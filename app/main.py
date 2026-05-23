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
    apply_bonus,
)

app = FastAPI(
    title="eRecommend: eSkolar Recommendation Engine back-end",
    description="Hybrid AI recommendation backend executing CHED regulatory weighting and semantic similarity analysis.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # Replace later with deployed URL and localhost
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

@app.get("/api/v1/health")
async def health():
    """ Check if the API is currently active. """
    return {
        "status": "healthy",
        "message": "eRecommend active."
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

        # Calculate CHED ranking
        academic_pts = get_academic_rating(student.gwa)
        income_pts = get_annual_gross_income_rating(student.annual_family_income)
        bonus_pts = apply_bonus(student.special_group)

        # Final Score
        eligibility_score = ((academic_pts * 0.70) + (income_pts * 0.30)) + bonus_pts

        results = generate_recommendations(
            eligibility_score=eligibility_score,
            student_profile=profile_text,
            student_annual_income=student.annual_family_income,
            student_grade=student.gwa,
            scholarships=scholarships
        )

        response: List[RecommendationResult] = []
        for res in results:
            response.append({
                "id": res['id'],
                "e_recommend": res['e_recommend'],
                'match': res['match'],
                'breakdown': {
                    'eligibility': round(res['eligibility'], 2),
                    'profile': round(res['profile'], 2),
                    'academic': academic_pts,
                    'income': income_pts,
                    'bonus': bonus_pts
                }
            })

        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"eRecommend engine error: {str(e)}")