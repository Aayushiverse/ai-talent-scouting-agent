"""
Engagement Module - Simulates conversational outreach with candidates
"""

import random
import re
from typing import Dict, List, Tuple

class ConversationEngine:
    """Simulates conversation with candidates to assess interest"""
    
    def __init__(self):
        self.conversation_history = {}
        self.questions = [
            {
                "id": "interest",
                "question": "Are you interested in this role?",
                "options": ["Yes, very interested", "Maybe, need more info", "No, not interested"],
                "scoring": {"Yes, very interested": 40, "Maybe, need more info": 20, "No, not interested": 0}
            },
            {
                "id": "salary",
                "question": "What is your expected annual salary (INR)?",
                "type": "range",
                "scoring": "dynamic"
            },
            {
                "id": "notice",
                "question": "What is your notice period?",
                "options": ["Immediate", "15 days", "30 days", "45 days", "60+ days"],
                "scoring": {"Immediate": 30, "15 days": 25, "30 days": 15, "45 days": 5, "60+ days": 0}
            },
            {
                "id": "relocation",
                "question": "Are you willing to relocate if needed?",
                "options": ["Yes", "No", "Depends on location"],
                "scoring": {"Yes": 15, "Depends on location": 8, "No": 0}
            },
            {
                "id": "reason",
                "question": "Why are you interested in this role?",
                "type": "text",
                "scoring": "keyword_based"
            }
        ]
    
    def start_conversation(self, candidate_id: str, candidate_name: str) -> Dict:
        """Initialize a new conversation"""
        self.conversation_history[candidate_id] = {
            "candidate_name": candidate_name,
            "candidate_id": candidate_id,
            "responses": {},
            "completed": False,
            "interest_score": 0
        }
        return {
            "conversation_id": candidate_id,
            "message": f"Hi {candidate_name}! I'm your AI recruiter. I have a role that might interest you. Can I ask you a few quick questions?",
            "next_question": self.questions[0]["question"],
            "options": self.questions[0].get("options", None)
        }
    
    def process_response(self, candidate_id: str, question_id: str, response: str) -> Dict:
        """Process candidate's response and return next question"""
        
        if candidate_id not in self.conversation_history:
            return {"error": "Conversation not found"}
        
        # Store response
        self.conversation_history[candidate_id]["responses"][question_id] = response
        
        # Find current question index
        current_q_index = next((i for i, q in enumerate(self.questions) if q["id"] == question_id), -1)
        
        # Check if there are more questions
        if current_q_index + 1 < len(self.questions):
            next_q = self.questions[current_q_index + 1]
            return {
                "message": "Thanks for your response!",
                "next_question": next_q["question"],
                "options": next_q.get("options", None),
                "is_complete": False
            }
        else:
            # Conversation complete - calculate score
            interest_score = self.calculate_interest_score(candidate_id)
            self.conversation_history[candidate_id]["completed"] = True
            self.conversation_history[candidate_id]["interest_score"] = interest_score
            
            return {
                "message": "Thank you for your time! I'll share your profile with the hiring team.",
                "next_question": None,
                "options": None,
                "is_complete": True,
                "interest_score": interest_score,
                "feedback": self.get_feedback(interest_score)
            }
    
    def calculate_interest_score(self, candidate_id: str) -> int:
        """Calculate final interest score from responses"""
        responses = self.conversation_history[candidate_id]["responses"]
        total_score = 0
        
        # Question 1: Basic interest (max 40 points)
        if "interest" in responses:
            interest_response = responses["interest"]
            for option, score in self.questions[0]["scoring"].items():
                if option.lower() in interest_response.lower():
                    total_score += score
                    break
        
        # Question 2: Salary expectation (dynamic, max 20 points)
        if "salary" in responses:
            salary_response = responses["salary"]
            try:
                # Extract number from response
                salary_num = int(re.sub(r'[^\d]', '', str(salary_response)))
                if salary_num <= 1500000:
                    total_score += 20
                elif salary_num <= 2000000:
                    total_score += 15
                elif salary_num <= 2500000:
                    total_score += 8
                else:
                    total_score += 0
            except:
                total_score += 10  # Default if can't parse
        
        # Question 3: Notice period (max 30 points)
        if "notice" in responses:
            notice_response = responses["notice"]
            for option, score in self.questions[2]["scoring"].items():
                if option.lower() in notice_response.lower():
                    total_score += score
                    break
        
        # Question 4: Relocation (max 10 points)
        if "relocation" in responses:
            relo_response = responses["relocation"]
            for option, score in self.questions[3]["scoring"].items():
                if option.lower() in relo_response.lower():
                    total_score += score
                    break
        
        # Question 5: Reason (keyword based, max 10 points)
        if "reason" in responses:
            reason = responses["reason"].lower()
            keywords = ["excited", "passionate", "growth", "learn", "challenge", "perfect", "match", "skills"]
            keyword_score = 0
            for keyword in keywords:
                if keyword in reason:
                    keyword_score += 2
            total_score += min(10, keyword_score)
        
        # Normalize to 0-100
        return min(100, total_score)
    
    def get_feedback(self, score: int) -> str:
        """Generate feedback based on interest score"""
        if score >= 80:
            return "🔥 High interest candidate - Strong alignment!"
        elif score >= 60:
            return "👍 Moderate interest - Worth pursuing"
        elif score >= 40:
            return "🤔 Low interest - May need more convincing"
        else:
            return "❌ Not interested - Remove from shortlist"
    
    def simulate_conversation(self, candidate: Dict, jd_skills: List[str]) -> Tuple[str, int]:
        """
        Simulate full conversation without UI (for batch processing)
        
        Args:
            candidate: Dictionary with candidate data
            jd_skills: List of skills from job description
        
        Returns:
            Tuple of (response_text, interest_score)
        """
        candidate_skills = candidate.get("Key Skills", "").lower()
        default_interest = candidate.get("Default Interest", "medium")
        notice_period = candidate.get("Notice Period", "30 days")
        salary = candidate.get("Salary Expectation (INR)", 1500000)
        
        # Convert salary to number if it's a string
        if isinstance(salary, str):
            salary = int(re.sub(r'[^\d]', '', salary))
        
        # Calculate skill match
        match_count = sum(1 for skill in jd_skills if skill.lower() in candidate_skills)
        match_percentage = (match_count / len(jd_skills)) * 100 if jd_skills else 0
        
        # Generate responses based on match and default interest
        responses = {}
        
        # Q1: Interest
        if match_percentage >= 60 and default_interest == "high":
            responses["interest"] = "Yes, very interested"
        elif match_percentage >= 40 or default_interest == "medium":
            responses["interest"] = "Maybe, need more info"
        else:
            responses["interest"] = "No, not interested"
        
        # Q2: Salary expectation
        responses["salary"] = str(salary)
        
        # Q3: Notice period
        responses["notice"] = notice_period
        
        # Q4: Relocation
        if candidate.get("Location", "") in ["Bangalore", "Mumbai", "Remote"]:
            responses["relocation"] = "Yes"
        else:
            responses["relocation"] = "Depends on location"
        
        # Q5: Reason
        if match_percentage >= 60:
            responses["reason"] = "This role perfectly matches my skills and career goals"
        elif match_percentage >= 30:
            responses["reason"] = "I'm excited about the opportunity to grow in this field"
        else:
            responses["reason"] = "I'm open to exploring new opportunities"
        
        # Store in history temporarily
        self.conversation_history["temp"] = {"responses": responses}
        score = self.calculate_interest_score("temp")
        del self.conversation_history["temp"]
        
        # Generate full response
        if responses["interest"] == "Yes, very interested":
            response_text = f"Yes, I'm very interested! My expected salary is {salary} INR, notice period is {notice_period}. This role aligns with my skills."
        elif responses["interest"] == "Maybe, need more info":
            response_text = f"Maybe interested. My expected salary is {salary} INR with {notice_period} notice. Could you share more details?"
        else:
            response_text = f"Not interested at this time. The role doesn't match my current preferences."
        
        return response_text, score


def generate_conversation(candidate: Dict, jd_skills: List[str]) -> List[Dict]:
    """Generate adaptive conversation based on candidate's interest level"""
    
    candidate_name = candidate.get("Name", "Candidate")
    candidate_skills = candidate.get("Key Skills", "").lower()
    default_interest = candidate.get("Default Interest", "medium")
    salary = candidate.get("Salary Expectation (INR)", 1500000)
    notice = candidate.get("Notice Period", "30 days")
    current_role = candidate.get("Current Role", "Professional")
    
    # Calculate match percentage
    match_count = sum(1 for skill in jd_skills if skill.lower() in candidate_skills)
    match_percentage = (match_count / len(jd_skills)) * 100 if jd_skills else 0
    
    # Determine interest level for branching
    if match_percentage >= 60 and default_interest == "high":
        interest_level = "high"
        interest_response = f"Yes, I'm very interested! As a {current_role}, this role aligns perfectly with my skills."
        reason_response = "I've been following your company's work in AI. This would be a great next step for my career."
        follow_up = "That's fantastic! Could you tell me what specifically attracted you to this role?"
    elif match_percentage >= 40 or default_interest == "medium":
        interest_level = "medium"
        interest_response = f"Maybe interested. I have some matching skills as a {current_role}, but I'd like to learn more."
        reason_response = "I'm looking for growth opportunities. Could you share more about the tech stack and team culture?"
        follow_up = "Of course! What aspects of the role are most important to you?"
    else:
        interest_level = "low"
        interest_response = f"Not really. The skill requirements don't align well with my current expertise."
        reason_response = "I'm keeping my options open, but this doesn't seem like a great fit."
        follow_up = "I understand. What kind of roles are you currently looking for?"
    
    if isinstance(salary, str):
      salary = int(salary.replace(',', '').replace('LPA', '').strip())
    salary_lpa = salary / 100000
    
    # Build adaptive conversation
    conversation = [
        {"speaker": "agent", "message": f"Hi {candidate_name}! I'm your AI recruiter. I found your profile and have a {', '.join(jd_skills[:3])} role. Are you interested?"},
        {"speaker": "candidate", "message": interest_response},
        {"speaker": "agent", "message": follow_up},
    ]
    
    # Branch based on interest level
    if interest_level == "high":
        conversation.extend([
            {"speaker": "candidate", "message": f"The tech stack and the opportunity to work on {jd_skills[0] if jd_skills else 'AI'} problems. Also, I've heard great things about your company culture."},
            {"speaker": "agent", "message": "Love the enthusiasm! What are your salary expectations?"},
            {"speaker": "candidate", "message": f"I'm expecting around {salary_lpa:.1f} LPA, but flexible for the right opportunity."},
        ])
    elif interest_level == "medium":
        conversation.extend([
            {"speaker": "candidate", "message": "I'd like to understand the team size, growth opportunities, and work-life balance."},
            {"speaker": "agent", "message": "Great questions! Let me clarify. What are your salary expectations?"},
            {"speaker": "candidate", "message": f"Looking at {salary_lpa:.1f} LPA, but would need to understand the full package."},
        ])
    else:
        conversation.extend([
            {"speaker": "candidate", "message": "Not much honestly. The skills don't match well."},
            {"speaker": "agent", "message": f"I appreciate your honesty. What's your notice period, just for reference?"},
            {"speaker": "candidate", "message": f"{notice}."},
        ])
    
    # Common remaining questions
    conversation.extend([
        {"speaker": "agent", "message": f"Understood. What's your notice period?"},
        {"speaker": "candidate", "message": f"{notice}. I can negotiate if needed."},
        {"speaker": "agent", "message": "Perfect! One last thing - what excites you about this opportunity?"},
        {"speaker": "candidate", "message": reason_response},
    ])
    
    # Closing message based on interest
    if interest_level == "high":
        closing = f"Thank you {candidate_name}! Based on our chat, you're a strong candidate. I'll fast-track your profile to the hiring team. Expect to hear from us within 48 hours!"
    elif interest_level == "medium":
        closing = f"Thanks {candidate_name}! I'll share more details about the role. Check your email for the complete JD and company info."
    else:
        closing = f"Thank you for your time {candidate_name}. I'll keep your profile for future roles that might be a better match."
    
    conversation.append({"speaker": "agent", "message": closing})
    
    return conversation


def calculate_interest_from_conversation(candidate: Dict, jd_skills: List[str]) -> int:
    """Calculate interest score based on conversation"""
    default_interest = candidate.get("Default Interest", "medium")
    candidate_skills = candidate.get("Key Skills", "").lower()
    notice = candidate.get("Notice Period", "30 days")
    
    # Calculate match percentage
    match_count = sum(1 for skill in jd_skills if skill.lower() in candidate_skills)
    match_percentage = (match_count / len(jd_skills)) * 100 if jd_skills else 0
    
    # Base score from match percentage (0-70 points)
    base_score = match_percentage * 0.7
    
    # Adjust with default interest (0-15 points)
    if default_interest == "high":
        base_score += 15
    elif default_interest == "medium":
        base_score += 8
    elif default_interest == "low":
        base_score += 0
    
    # Notice period adjustment (0-15 points)
    notice_str = str(notice)
    if "15" in notice_str or "immediate" in notice_str.lower():
        base_score += 15
    elif "30" in notice_str:
        base_score += 10
    elif "45" in notice_str:
        base_score += 5
    elif "60" in notice_str or "90" in notice_str:
        base_score += 0
    
    return max(0, min(100, int(base_score)))

def simulate_candidate_engagement(candidate: Dict, jd_skills: List[str]) -> Dict:
    """
    Quick function to simulate engagement
    
    Returns:
        Dictionary with response and score
    """
    engine = ConversationEngine()
    response, score = engine.simulate_conversation(candidate, jd_skills)
    return {
        "candidate_id": candidate.get("ID", "Unknown"),
        "candidate_name": candidate.get("Name", "Unknown"),
        "response": response,
        "interest_score": score,
        "recommendation": engine.get_feedback(score)
    }


def get_engagement_questions() -> List[Dict]:
    """Get list of engagement questions for UI"""
    engine = ConversationEngine()
    return engine.questions


# Example usage
if __name__ == "__main__":
    # Test the engagement engine
    
    # Sample candidate
    test_candidate = {
        "ID": "C001",
        "Name": "Priya Sharma",
        "Current Role": "Senior Data Scientist",
        "Key Skills": "Python, TensorFlow, SQL, NLP, AWS",
        "Location": "Bangalore",
        "Notice Period": "30 days",
        "Default Interest": "high",
        "Salary Expectation (INR)": 2200000
    }
    
    jd_skills = ["python", "sql", "machine learning", "aws"]
    
    print("=" * 60)
    print("ENGAGEMENT MODULE TEST")
    print("=" * 60)
    
    # Test 1: Generate conversation
    print("\n📞 GENERATED CONVERSATION:")
    print("-" * 40)
    conversation = generate_conversation(test_candidate, jd_skills)
    for msg in conversation:
        speaker = "🤖 Agent" if msg["speaker"] == "agent" else f"👤 {test_candidate['Name']}"
        print(f"{speaker}: {msg['message']}\n")
    
    # Test 2: Calculate interest score
    print("\n📊 INTEREST SCORE CALCULATION:")
    print("-" * 40)
    score = calculate_interest_from_conversation(test_candidate, jd_skills)
    print(f"Interest Score: {score}/100")
    
    # Test 3: Simulate engagement
    print("\n🎯 ENGAGEMENT SIMULATION:")
    print("-" * 40)
    result = simulate_candidate_engagement(test_candidate, jd_skills)
    print(f"Candidate: {result['candidate_name']}")
    print(f"Response: {result['response']}")
    print(f"Score: {result['interest_score']}")
    print(f"Recommendation: {result['recommendation']}")
    
    print("\n✅ Engagement module ready!")