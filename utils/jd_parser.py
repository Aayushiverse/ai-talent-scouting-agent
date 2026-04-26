"""
JD Parser Module - Extracts skills, experience, and requirements from Job Descriptions
"""

import re
from typing import List, Dict, Tuple

# Common tech skills database - EXPANDED with common variations
SKILLS_DATABASE = {
    "programming_languages": [
        "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "go", "rust", 
        "swift", "kotlin", "php", "scala", "r", "matlab", "perl", "haskell", "dart"
    ],
    "frameworks_libraries": [
        "react", "angular", "vue", "django", "flask", "fastapi", "spring", "springboot",
        "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy", "matplotlib",
        "selenium", "beautifulsoup", "requests", "asyncio", "celery", "redis", "rabbitmq",
        "node.js", "express", "next.js", "gatsby", "flutter", "xamarin", "unity"
    ],
    "databases": [
        "sql", "mysql", "postgresql", "mongodb", "cassandra", "redis", "elasticsearch",
        "dynamodb", "oracle", "mssql", "sqlite", "firebase", "couchdb", "neo4j",
        "postgres", "nosql"
    ],
    "cloud_devops": [
        "aws", "ec2", "s3", "lambda", "rds", "cloudformation", "azure", "gcp", "google cloud",
        "docker", "kubernetes", "jenkins", "gitlab ci", "github actions", "terraform",
        "ansible", "prometheus", "grafana", "datadog", "newrelic", "splunk",
        "cloud", "sagemaker"
    ],
    "data_science_ml": [
        "machine learning", "deep learning", "nlp", "natural language processing", 
        "computer vision", "llm", "large language models", "gpt", "bert", "transformers",
        "data science", "data analysis", "statistics", "probability", "linear algebra",
        "a/b testing", "hypothesis testing", "regression", "classification", "clustering",
        "ml", "dl", "neural networks", "xgboost", "scikit-learn", "sklearn",
        "tensorflow", "pytorch", "keras", "pandas", "numpy"
    ],
    "big_data": [
        "hadoop", "spark", "hive", "kafka", "flink", "storm", "airflow", "databricks",
        "snowflake", "bigquery", "redshift"
    ],
    "frontend": [
        "html", "css", "sass", "less", "tailwind", "bootstrap", "material-ui", "ant design",
        "webpack", "babel", "vite", "rollup"
    ],
    "mobile": [
        "android", "ios", "react native", "flutter", "swift", "kotlin", "objective-c",
        "xcode", "android studio"
    ]
}

# Flatten skills for easier lookup
ALL_SKILLS = set()
for category in SKILLS_DATABASE.values():
    ALL_SKILLS.update(category)

# Add common variations
SKILL_VARIATIONS = {
    "nlp": ["natural language processing", "nlp"],
    "ml": ["machine learning", "ml"],
    "dl": ["deep learning", "dl"],
    "sql": ["sql", "postgresql", "mysql"],
    "aws": ["aws", "amazon web services"],
}


class JDParser:
    """Job Description Parser class"""
    
    def __init__(self):
        self.jd_text = ""
        self.extracted_skills = []
        self.extracted_experience = 0
        self.extracted_location = ""
        self.extracted_education = ""
        
    def parse(self, jd_text: str) -> Dict:
        """
        Main method to parse job description
        """
        self.jd_text = jd_text.lower()
        
        return {
            "skills": self.extract_skills(),
            "experience": self.extract_experience(),
            "location": self.extract_location(),
            "education": self.extract_education(),
            "job_title": self.extract_job_title(),
            "responsibilities": self.extract_responsibilities(),
            "requirements": self.extract_requirements()
        }
    
    def extract_skills(self) -> List[str]:
        """Extract technical skills from JD - IMPROVED"""
        found_skills = set()
        jd_lower = self.jd_text
        
        # Check each skill in database
        for skill in ALL_SKILLS:
            if skill in jd_lower:
                # Map variations to standard names
                if skill == "natural language processing":
                    found_skills.add("nlp")
                elif skill == "machine learning":
                    found_skills.add("machine learning")
                elif skill == "deep learning":
                    found_skills.add("deep learning")
                else:
                    found_skills.add(skill)
        
        # Check for variations
        if "natural language processing" in jd_lower or "nlp" in jd_lower:
            found_skills.add("nlp")
        
        if "machine learning" in jd_lower or "ml" in jd_lower:
            found_skills.add("machine learning")
        
        if "deep learning" in jd_lower or "dl" in jd_lower:
            found_skills.add("deep learning")
        
        # Specific checks for common skills in your JD
        if "python" in jd_lower:
            found_skills.add("python")
        
        if "sql" in jd_lower or "postgresql" in jd_lower or "mysql" in jd_lower:
            found_skills.add("sql")
        
        if "aws" in jd_lower or "amazon web services" in jd_lower:
            found_skills.add("aws")
        
        if "tensorflow" in jd_lower:
            found_skills.add("tensorflow")
        
        if "pytorch" in jd_lower:
            found_skills.add("pytorch")
        
        if "spark" in jd_lower:
            found_skills.add("spark")
        
        if "docker" in jd_lower:
            found_skills.add("docker")
        
        if "kubernetes" in jd_lower or "k8s" in jd_lower:
            found_skills.add("kubernetes")
        
        self.extracted_skills = list(found_skills)
        return self.extracted_skills
    
    def extract_experience(self) -> float:
        """Extract required years of experience"""
        patterns = [
            r'(\d+)[\+]?\s*(?:years?|yrs?)\s+of\s+experience',
            r'experience\s*:\s*(\d+)[\+]?\s*(?:years?|yrs?)',
            r'(\d+)[\+]?\s*(?:years?|yrs?)\s+experience',
            r'minimum\s+(\d+)[\+]?\s*(?:years?|yrs?)',
            r'at\s+least\s+(\d+)[\+]?\s*(?:years?|yrs?)',
            r'(\d+)[\+]?\s*\+\s*(?:years?|yrs?)',
            r'(\d+)[\+]?\s*years?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.jd_text)
            if match:
                self.extracted_experience = float(match.group(1))
                return self.extracted_experience
        
        self.extracted_experience = 0
        return 0
    
    def extract_location(self) -> str:
        """Extract job location"""
        location_keywords = ['bangalore', 'mumbai', 'delhi', 'gurgaon', 'hyderabad', 
                            'chennai', 'pune', 'kolkata', 'remote', 'work from home',
                            'hybrid', 'onsite']
        
        for location in location_keywords:
            if location in self.jd_text:
                self.extracted_location = location.title()
                return self.extracted_location
        
        self.extracted_location = "Not specified"
        return "Not specified"
    
    def extract_education(self) -> str:
        """Extract education requirements"""
        education_patterns = [
            (r'b\.?tech|bachelor.?s?\s+of\s+technology', "B.Tech"),
            (r'b\.?e|bachelor.?s?\s+of\s+engineering', "B.E"),
            (r'b\.?sc|bachelor.?s?\s+of\s+science', "B.Sc"),
            (r'm\.?tech|master.?s?\s+of\s+technology', "M.Tech"),
            (r'm\.?e|master.?s?\s+of\s+engineering', "M.E"),
            (r'm\.?sc|master.?s?\s+of\s+science', "M.Sc"),
            (r'ph\.?d|doctorate', "PhD"),
            (r'[mb]ca|computer\s+applications', "MCA/BCA"),
            (r'bachelor.?s?\s+degree', "Bachelor's Degree"),
            (r'master.?s?\s+degree', "Master's Degree")
        ]
        
        for pattern, degree in education_patterns:
            if re.search(pattern, self.jd_text):
                self.extracted_education = degree
                return self.extracted_education
        
        self.extracted_education = "Not specified"
        return "Not specified"
    
    def extract_job_title(self) -> str:
        """Extract job title from JD"""
        title_patterns = [
            r'(?:hiring|looking for|role:|position:|title:)\s+([A-Za-z\s]+?)(?:\n|\.|,)',
            r'job\s+title\s*:\s*([A-Za-z\s]+)',
            r'^([A-Za-z\s]+?)(?:\n|at\s|for\s)'
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, self.jd_text, re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                if len(title) > 5 and len(title) < 50:
                    return title.title()
        
        return "Not specified"
    
    def extract_responsibilities(self) -> List[str]:
        """Extract key responsibilities"""
        responsibilities = []
        
        bullet_pattern = r'[•\-*]\s*([^.•\n]+)'
        number_pattern = r'\d+\.\s*([^\n]+)'
        
        matches = re.findall(bullet_pattern, self.jd_text)
        if not matches:
            matches = re.findall(number_pattern, self.jd_text)
        
        responsibility_keywords = ['develop', 'design', 'implement', 'manage', 'lead', 
                                  'create', 'build', 'maintain', 'optimize', 'test', 
                                  'deploy', 'monitor', 'analyze', 'collaborate']
        
        for match in matches[:5]:
            if any(keyword in match.lower() for keyword in responsibility_keywords):
                responsibilities.append(match.strip())
        
        return responsibilities
    
    def extract_requirements(self) -> List[str]:
        """Extract key requirements"""
        requirements = []
        
        try:
            req_section = re.search(r'(?:requirements|qualifications|what you need)[:\s]*([^]+?)(?:\n\n|\n$|\Z)', 
                            self.jd_text, re.IGNORECASE | re.MULTILINE)
            
            if req_section:
                req_text = req_section.group(1)
                bullet_pattern = r'[•\-*]\s*([^.•\n]+)'
                matches = re.findall(bullet_pattern, req_text)
                
                for match in matches[:5]:
                    requirements.append(match.strip())
        except Exception:
            lines = self.jd_text.split('\n')
            in_req_section = False
            for line in lines:
                if any(keyword in line.lower() for keyword in ['requirements', 'qualifications']):
                    in_req_section = True
                    continue
                if in_req_section and line.strip() and not line.strip().startswith('•'):
                    if len(requirements) < 5:
                        requirements.append(line.strip())
                if in_req_section and not line.strip():
                    break
        
        return requirements


def clean_jd_text(raw_text: str) -> str:
    """Clean and normalize JD text"""
    cleaned = re.sub(r'\s+', ' ', raw_text)
    cleaned = re.sub(r'[^\w\s\.\,\-\#\+]', '', cleaned)
    return cleaned.strip()


def get_match_explanation(jd_skills: List[str], candidate_skills: List[str]) -> Dict:
    """Generate explanation for skill match"""
    jd_set = set(jd_skills)
    candidate_set = set(candidate_skills)
    
    return {
        "matched_skills": list(jd_set.intersection(candidate_set)),
        "missing_skills": list(jd_set - candidate_set),
        "extra_skills": list(candidate_set - jd_set),
        "match_percentage": round((len(jd_set.intersection(candidate_set)) / len(jd_set)) * 100, 2) if jd_set else 0
    }


def parse_job_description(jd_text: str) -> Dict:
    """Quick function to parse JD without creating class instance"""
    parser = JDParser()
    return parser.parse(jd_text)


if __name__ == "__main__":
    # Test the parser
    sample_jd = """
    Senior Data Scientist needed. Skills: Python, SQL, Machine Learning, Deep Learning, NLP, AWS.
    Experience: 4+ years. Location: Bangalore.
    """
    
    result = parse_job_description(sample_jd)
    
    print("=" * 50)
    print("JD PARSER OUTPUT")
    print("=" * 50)
    print(f"Skills: {', '.join(result['skills'])}")
    print(f"Experience: {result['experience']} years")
    print(f"Location: {result['location']}")