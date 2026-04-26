# AI-Powered Talent Scouting & Engagement Agent

An intelligent agent that automates recruiter workflow - from parsing job descriptions to matching candidates, simulating conversations, and generating ranked shortlists.

## Features

- JD Parsing - Extracts skills, experience, location from job descriptions
- Candidate Matching - Compares candidate skills with JD requirements with explainability
- Interest Simulation - Conversational AI to assess candidate interest
- Ranked Output - Weighted score (60% Match + 40% Interest)
- Recruiter Insights Hub - One-click analytics and outreach emails

## Tech Stack

- Python 3.13
- Streamlit
- Pandas
- OpenAI API (optional)

## Installation

Install dependencies:

pip install -r requirements.txt

Run the application:

streamlit run app.py


## 📊 Scoring Logic

| Score Type     | Weight | Description                                      |
|----------------|--------|--------------------------------------------------|
| Match Score    | 60%    | Skills match between JD and candidate            |
| Interest Score | 40%    | Simulated candidate interest level               |
| Final Score    | 100%   | (Match × 0.6) + (Interest × 0.4)                 |

---

## 🏆 Ranking Scale

| Rank | Score Range | Action                    |
|------|------------|---------------------------|
| A+   | 85–100     | Contact immediately       |
| A    | 70–84      | Schedule screening call   |
| B    | 55–69      | Keep in shortlist         |
| C    | 40–54      | Consider as backup        |
| D    | Below 40   | Remove from list          |

---

## 📁 Project Structure


ai-talent-scouting-agent/
├── app.py
├── candidates.csv
├── requirements.txt
├── README.md
├── .gitignore
├── utils/
│   ├── __init__.py
│   ├── jd_parser.py
│   ├── matcher.py
│   ├── scoring.py
│   └── engagement.py
└── .streamlit/
    └── secrets.toml

---

## 🧪 Sample Input

**Job Description:**

Data Scientist needed. Skills: Python, SQL, Machine Learning, NLP, AWS.  
Experience: 4+ years. Location: Bangalore.

## 📤 Sample Output

**Ranked Shortlist:**

| Name          | Role                   | Final Score | Rank |
|---------------|------------------------|------------|------|
| Priya Sharma  | Senior Data Scientist  | 82         | A    |
| Meera Iyer    | AI Engineer            | 76         | A    |
| Divya Menon   | Lead Data Analyst      | 70         | A    |

---

## 🎥 Demo Video

[Add your demo video link here]

---

## 🧠 Architecture

The agent follows a 5-step pipeline:

1. **JD Parsing** – Extract skills and requirements  
2. **Candidate Loading** – Load candidates from CSV database  
3. **Skill Matching** – Compare JD skills with candidate profiles  
4. **Interest Simulation** – Rule-based conversation simulation  
5. **Ranking** – Weighted scoring and sorting  

---

## 📌 Submission Details

- **Project:** Catalyst Hackathon - Deccan AI  
- **GitHub Username:** Aayushiverse  
- **Repository:** https://github.com/Aayushiverse/ai-talent-scouting-agent  

---

## 📄 License

This project is licensed under the MIT License.
