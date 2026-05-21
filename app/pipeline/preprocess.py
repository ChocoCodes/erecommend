from app.schemas import StudentProfile

def standardized_grade_percentage(gwa: float) -> float:
    """ 
        Transforms a 1.0 - 5.0 grade_percentage metric scale into a standardized percentage value.
        Result = 100 - ((grade_percentage - 1) * 10.0)
    """
    if gwa < 1.0 or gwa > 5.0: return 75.0
    return round(100.0 - ((gwa - 1) * 10.0), 2)

def compile_profile_text(profile: StudentProfile) -> str:
    """ Concatenates profile features into a rich text string optimized for embedding arrays. """
    blocks = [
        f"Student Profile for { profile.full_name }",
        f"Personal Background: { profile.bio } located in { profile.city }, { profile.region }",
        f"Highest Education: { profile.highest_degree }"
    ]

    categories = {}
    for item in profile.profile_items:
        cat = item.category.lower()
        detail = f"'{item.title}'"
        if item.description: detail += f" ({item.description})"
        entity = item.issuer or item.organization
        if entity: detail += f" at {entity}"
        categories.setdefault(cat, []).append(detail)
        
    for cat, details in categories.items():
        blocks.append(f"{cat.replace('_', ' ').capitalize()}: {'; '.join(details)}.")
    
    profile_compiled = " ".join(blocks)
    return profile_compiled

def get_academic_rating(grade_percentage: float) -> int:
    """
        Rate a student's grade percentage according to CHED scoring guidelines.
    """
    if grade_percentage > 99.0 and grade_percentage <= 100.0: return 100
    elif grade_percentage >= 97.0: return 95
    elif grade_percentage >= 95.0: return 90
    elif grade_percentage >= 93.0: return 85
    elif grade_percentage >= 91.0: return 80
    else: return 75

def get_annual_gross_income_rating(annual_gross_income: float) -> int:
    """
        Rate a student's family annual gross income according to CHED scoring guidelines.
    """
    if annual_gross_income > 0.0 and annual_gross_income <= 70000.0: return 100
    elif annual_gross_income > 70000.0 and annual_gross_income <= 136000.0: return 95
    elif annual_gross_income > 136000.0 and annual_gross_income <= 202000.0: return 90
    elif annual_gross_income > 202000.0 and annual_gross_income <= 268000.0: return 85
    elif annual_gross_income > 268000.0 and annual_gross_income <= 334000.0: return 80
    else: return 75

def apply_bonus(student_special_group: str | None) -> int: 
    """
        Additional 5 points for applicants belonging to the special groups:
        RA 7279, RA 7277, RA 8972, RA 9994, RA 8371 
    """
    special_groups = [
        'Persons with Disabilities (PWD)', 
        'Underpriviledged and Homeless Citizens', 
        'Indigenous People',
        'Solo Parent', 
        'Solo Parent Dependent'
    ]

    if student_special_group is None: return 0
    return 5 if student_special_group in special_groups else 0

def get_match_category(rating: float) -> str:
    if rating >= 88.0: return "strong"
    elif rating >= 75.0: return "good"
    else: return "fair"
    