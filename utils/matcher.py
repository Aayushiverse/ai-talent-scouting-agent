"""
Matcher Module - Smart Skill Matching Logic (Upgraded)
"""

from typing import List, Tuple, Dict

# -----------------------------------------
# Synonym & Abbreviation Map (Covers your dataset)
# -----------------------------------------
SKILL_SYNONYMS = {
    # Core DS/ML
    "machine learning": ["ml", "machine-learning"],
    "deep learning": ["dl", "deep-learning"],
    "natural language processing": ["nlp", "natural-language-processing"],
    "llms": ["large language models", "llm"],
    "statistics": ["statistical analysis"],

    # Languages
    "python": ["py"],
    "java": [],
    "c++": ["cpp"],

    # ML Libraries
    "scikit-learn": ["sklearn", "scikit learn"],
    "pandas": [],
    "numpy": ["np"],
    "xgboost": ["xg boost"],
    "pytorch": ["py torch", "torch"],
    "tensorflow": ["tensor flow"],
    "huggingface": ["hugging face"],
    "bert": [],
    "cnn": ["convolutional neural network", "cnns"],
    "opencv": ["open cv"],
    "mlflow": ["ml flow"],

    # Cloud & MLOps
    "aws": ["amazon web services", "s3", "lambda", "sagemaker"],
    "cloud": ["gcp", "azure", "cloud computing"],
    "mlops": ["ml ops"],
    "docker": [],
    "kubernetes": ["k8s"],
    "ci/cd": ["cicd", "continuous integration", "continuous delivery"],

    # Data Engineering
    "spark": ["pyspark", "apache spark"],
    "kafka": ["apache kafka"],
    "airflow": ["apache airflow"],
    "snowflake": [],

    # Analytics / BI
    "tableau": [],
    "power bi": ["powerbi"],
    "excel": ["microsoft excel"],

    # Backend / Web
    "spring boot": ["springboot"],
    "microservices": ["micro services"],
    "rest apis": ["rest api", "rest"],
    "flask": [],
    "node.js": ["nodejs", "node"],
    "react": ["reactjs", "react.js"],
    "mongodb": ["mongo db"],

    # Leadership / Strategy
    "ai strategy": ["ai leadership", "data strategy"],
    "leadership": ["team leadership", "people management"],
}

def normalize(skill: str) -> str:
    return skill.lower().strip()

def expand_skill(skill: str) -> List[str]:
    """Return list of synonyms for a skill (canonical + variants)."""
    skill = normalize(skill)
    synonyms = SKILL_SYNONYMS.get(skill, [])
    return [skill] + synonyms

# -----------------------------------------
# SMART MATCHING FUNCTION
# -----------------------------------------
def calculate_match_score(jd_skills: List[str], candidate_skills_str: str) -> Tuple[float, List[str], List[str]]:
    """
    Smart skill matching with synonyms, abbreviations & fuzzy matching.
    """
    candidate_skills = [normalize(s) for s in candidate_skills_str.split(",")]

    matched = []
    missing = []

    for jd_skill in jd_skills:
        expanded = expand_skill(jd_skill)
        found = False

        for synonym in expanded:
            for cand_skill in candidate_skills:
                # Fuzzy match: substring or reverse substring
                if synonym in cand_skill or cand_skill in synonym:
                    matched.append(jd_skill.lower())
                    found = True
                    break
            if found:
                break

        if not found:
            missing.append(jd_skill.lower())

    total = len(matched) + len(missing)
    score = (len(matched) / total) * 100 if total > 0 else 0

    return round(score, 2), matched, missing

# -----------------------------------------
# EXPERIENCE MATCH (unchanged)
# -----------------------------------------
def calculate_experience_match(jd_experience: float, candidate_experience: float) -> float:
    if jd_experience == 0:
        return 100
    if candidate_experience >= jd_experience:
        return 100
    elif candidate_experience >= jd_experience * 0.8:
        return 80
    elif candidate_experience >= jd_experience * 0.6:
        return 60
    elif candidate_experience >= jd_experience * 0.4:
        return 40
    else:
        return 20

# -----------------------------------------
# LOCATION MATCH (unchanged)
# -----------------------------------------
def calculate_location_match(jd_location: str, candidate_location: str) -> float:
    jd_loc = jd_location.lower()
    cand_loc = candidate_location.lower()

    if jd_loc == cand_loc:
        return 100
    elif "remote" in jd_loc or "hybrid" in jd_loc:
        return 90
    elif cand_loc in jd_loc or jd_loc in cand_loc:
        return 70
    else:
        return 50

# -----------------------------------------
# MATCH EXPLANATION (unchanged)
# -----------------------------------------
def get_match_explanation(matched_skills: List[str], missing_skills: List[str]) -> Dict:
    return {
        "summary": f"Matched {len(matched_skills)} out of {len(matched_skills) + len(missing_skills)} skills",
        "strengths": f"Has skills: {', '.join(matched_skills)}" if matched_skills else "No skill matches",
        "gaps": f"Missing skills: {', '.join(missing_skills)}" if missing_skills else "No missing skills",
        "match_percentage": round((len(matched_skills) / (len(matched_skills) + len(missing_skills))) * 100, 2)
        if (matched_skills or missing_skills) else 0
    }
