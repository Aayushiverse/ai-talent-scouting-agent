"""
Scoring Module - Handles interest scoring and final ranking logic
"""

from typing import Dict, List

class InterestScorer:
    """Calculates interest scores based on candidate responses"""
    
    def __init__(self):
        self.weights = {
            "interest": 0.40,
            "salary": 0.20,
            "notice": 0.20,
            "relocation": 0.10,
            "reason": 0.10
        }
    
    def calculate_interest_score(self, responses: Dict) -> int:
        """Calculate interest score from candidate responses"""
        scores = {
            "interest": self._score_interest(responses.get("interest", "")),
            "salary": self._score_salary(responses.get("salary", "")),
            "notice": self._score_notice(responses.get("notice", "")),
            "relocation": self._score_relocation(responses.get("relocation", "")),
            "reason": self._score_reason(responses.get("reason", ""))
        }
        
        total_score = 0
        for key, score in scores.items():
            total_score += score * self.weights[key]
        
        return int(total_score)
    
    def _score_interest(self, response: str) -> float:
        response_lower = response.lower()
        if "very interested" in response_lower or "yes" in response_lower:
            return 100
        elif "maybe" in response_lower or "need more info" in response_lower:
            return 60
        elif "no" in response_lower or "not interested" in response_lower:
            return 0
        else:
            return 50
    
    def _score_salary(self, response: str) -> float:
        try:
            import re
            salary_num = int(re.sub(r'[^\d]', '', str(response)))
            if salary_num <= 1500000:
                return 100
            elif salary_num <= 2000000:
                return 75
            elif salary_num <= 2500000:
                return 50
            elif salary_num <= 3000000:
                return 25
            else:
                return 0
        except:
            return 50
    
    def _score_notice(self, response: str) -> float:
        response_lower = str(response).lower()
        if "immediate" in response_lower:
            return 100
        elif "15 days" in response_lower:
            return 90
        elif "30 days" in response_lower:
            return 70
        elif "45 days" in response_lower:
            return 50
        elif "60" in response_lower or "90" in response_lower:
            return 30
        else:
            return 50
    
    def _score_relocation(self, response: str) -> float:
        response_lower = response.lower()
        if "yes" in response_lower:
            return 100
        elif "depends" in response_lower:
            return 60
        elif "no" in response_lower:
            return 0
        else:
            return 50
    
    def _score_reason(self, response: str) -> float:
        response_lower = response.lower()
        keywords = ["excited", "passionate", "growth", "learn", "challenge", "perfect", "match", "skills"]
        score = 0
        for keyword in keywords:
            if keyword in response_lower:
                score += 12.5
        return min(100, score)


def calculate_final_score(match_score, interest_score, match_weight=0.6, interest_weight=0.4):
    """Calculate final weighted score - handles string inputs SAFELY"""
    # Convert to float with proper error handling
    try:
        match_score = float(match_score) if match_score is not None else 0
    except (ValueError, TypeError):
        match_score = 0
    
    try:
        interest_score = float(interest_score) if interest_score is not None else 0
    except (ValueError, TypeError):
        interest_score = 0
    
    return (match_score * match_weight) + (interest_score * interest_weight)


def get_rank_description(score):
    """Get description and recommendation based on score"""
    # Convert to float safely
    try:
        score = float(score) if score is not None else 0
    except (ValueError, TypeError):
        score = 0
    
    if score >= 85:
        return {
            "rank": "A+",
            "description": "Excellent fit! Strong skills and high interest",
            "action": "Contact immediately for interview"
        }
    elif score >= 70:
        return {
            "rank": "A",
            "description": "Good fit with solid interest",
            "action": "Schedule screening call"
        }
    elif score >= 55:
        return {
            "rank": "B",
            "description": "Moderate fit - worth considering",
            "action": "Keep in shortlist for now"
        }
    elif score >= 40:
        return {
            "rank": "C",
            "description": "Low fit - skill gaps or low interest",
            "action": "Consider as backup only"
        }
    else:
        return {
            "rank": "D",
            "description": "Poor fit - significant gaps",
            "action": "Remove from shortlist"
        }


def calculate_scores(match_score, interest_score):
    """Quick function to calculate all scores"""
    final_score = calculate_final_score(match_score, interest_score)
    rank_info = get_rank_description(final_score)
    
    return {
        "match_score": match_score,
        "interest_score": interest_score,
        "final_score": final_score,
        "rank": rank_info["rank"],
        "description": rank_info["description"],
        "action": rank_info["action"]
    }