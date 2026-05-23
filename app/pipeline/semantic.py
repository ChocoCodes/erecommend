import numpy as np 
from sentence_transformers import SentenceTransformer
from app.schemas import Scholarship
from typing import List, Dict, Any
from app.pipeline.preprocess import get_match_category
from app.pipeline.preprocess import preprocess_scholarship 

print("Loading SentenceTransformer ('all-MiniLM-L6-v2')...")
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding(text: str) -> np.ndarray:
    """
    Generate a 384-dimensional dense float vector embedding for a given text block.
    """
    if not text or not text.strip():
        return np.zeros(384)
    return model.encode(text, convert_to_numpy = True)

def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """
    Compute the Cosine Similarity between two vector arrays.
    Returns a float value between -1.0 and 1.0 (normalized to 0.0 - 1.0 in application).
    How similiar are the student profile and the scholarship description?
    """

    dot = np.dot(vec_a, vec_b)
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)

    if norm_a == 0 or norm_b == 0:
        return 0.0
    
    return float(dot / (norm_a * norm_b))

def generate_recommendations(
        eligibility_score: float, 
        student_profile: str, 
        student_annual_income: float,
        student_grade: float,
        scholarships: List[Scholarship]
    ) -> List[Dict[str, Any]]:
    """
    Calculate eRecommend rating and corresponding match category for each scholarships.
    """

    student_vector = get_embedding(student_profile)
    recommendations = []

    for s in scholarships:
        if s.status.lower() != "ongoing": continue 
        if s.annual_family_income is not None:
            # If student's background family income exceeds the scholarship's cap, drop it
            if student_annual_income > s.annual_family_income:
                continue
        if student_grade < s.cutoff_grade:
            continue
        
        scholarship_text = preprocess_scholarship(s)
        scholarship_vector = get_embedding(scholarship_text)
        similarity = cosine_similarity(student_vector, scholarship_vector)

        semantic_score_weighted = max(0.0, similarity * 100.0) * 0.40
        eligibility_score_weighted = (eligibility_score * 0.60)
        final_score = eligibility_score_weighted + semantic_score_weighted

        match = get_match_category(final_score)

        recommendations.append({
            "id": s.id,
            "e_recommend": round(final_score, 2),
            "match": match,
            'eligibility': eligibility_score_weighted,
            "profile": semantic_score_weighted
        })
    
    recommendations.sort(key=lambda x: x['e_recommend'], reverse=True)
    return recommendations
