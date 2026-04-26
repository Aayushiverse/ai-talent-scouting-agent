"""
AI-Powered Talent Scouting & Engagement Agent
Main Streamlit Application
"""

import streamlit as st
import pandas as pd
import os
from openai import OpenAI

# Import from utils modules
from utils.jd_parser import parse_job_description
from utils.matcher import calculate_match_score, get_match_explanation
from utils.matcher import SKILL_SYNONYMS, expand_skill
from utils.scoring import InterestScorer, calculate_final_score, get_rank_description
from utils.engagement import generate_conversation, calculate_interest_from_conversation

# -------------------------------
# Initialize OpenAI Client
# -------------------------------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# -------------------------------
# File path setup
# -------------------------------
BASE_DIR = os.path.dirname(__file__)
file_path = os.path.join(BASE_DIR, "candidates.csv")

# -------------------------------
# Helper Functions
# -------------------------------

def extract_jd_info(jd_text):
    """Extract skills using upgraded synonym-aware matching"""
    jd_lower = jd_text.lower()

    # Use the SAME skills as your matcher
    all_skills = list(SKILL_SYNONYMS.keys())

    detected = []
    for skill in all_skills:
        for keyword in expand_skill(skill):
            if keyword in jd_lower:
                detected.append(skill)
                break

    detected = list(dict.fromkeys(detected))

    if not detected:
        detected = ["python", "sql"]

    st.session_state['parsed_jd'] = {"skills": detected}
    return detected

def simulate_candidate_response(row, jd_skills, jd_text):
    """Simulate interest using upgraded fuzzy matching"""
    
    default_interest = row.get("Default Interest", "medium")
    candidate_skills = row["Key Skills"]

    # Use upgraded matcher for match count
    match_score, matched, missing = calculate_match_score(jd_skills, candidate_skills)

    if match_score >= 60:
        if default_interest == "high":
            return "Yes, very interested! This role perfectly matches my skills and career goals."
        elif default_interest == "medium":
            return "Yes, I'm interested. Would like to learn more about the team and projects."
        else:
            return "Maybe interested. I have some matching skills but need more information."
    elif match_score >= 30:
        return "Maybe interested. I have some relevant skills but not a perfect match."
    else:
        return "Not interested at this time. The skill requirements don't align with my expertise."

def get_interest_score_from_response(response, row, jd_skills):
    """Calculate interest score with reasoning tags"""
    
    response_lower = response.lower()
    notice_period = row.get("Notice Period", "30 days")
    default_interest = row.get("Default Interest", "medium")
    
    # Track reasoning
    reasoning = []
    
    # Base score from response with reasoning
    if "very interested" in response_lower:
        base_score = 90
        reasoning.append("🗣️ Candidate expressed strong interest verbally")
    elif "interested" in response_lower:
        base_score = 75
        reasoning.append("🗣️ Candidate showed positive interest")
    elif "maybe" in response_lower:
        base_score = 60
        reasoning.append("🤔 Candidate wants more information before deciding")
    else:
        base_score = 30
        reasoning.append("😐 Candidate showed low enthusiasm")
    
    # Adjust for notice period
    notice_adjustment = 0
    if "immediate" in notice_period.lower() or "15 days" in notice_period:
        notice_adjustment = 10
        reasoning.append("⏱️ Short notice period (+10 points)")
    elif "30 days" in notice_period:
        notice_adjustment = 5
        reasoning.append("📅 Standard notice period (+5 points)")
    elif "60 days" in notice_period or "90 days" in notice_period:
        notice_adjustment = -10
        reasoning.append("⚠️ Long notice period (-10 points)")
    
    # Adjust for default interest
    interest_adjustment = 0
    if default_interest == "high":
        interest_adjustment = 5
        reasoning.append("📊 Profile indicates high job-seeking activity (+5)")
    elif default_interest == "low":
        interest_adjustment = -10
        reasoning.append("📊 Profile indicates passive job seeker (-10)")
    
    # Calculate skill match impact
    candidate_skills = row["Key Skills"].lower()
    match_count = sum(1 for skill in jd_skills if skill.lower() in candidate_skills)
    match_percentage = (match_count / len(jd_skills)) * 100 if jd_skills else 0
    
    if match_percentage >= 60:
        reasoning.append(f"🎯 {match_count}/{len(jd_skills)} skills match - strong alignment")
    elif match_percentage >= 30:
        reasoning.append(f"📊 {match_count}/{len(jd_skills)} skills match - partial alignment")
    else:
        reasoning.append(f"⚠️ Only {match_count}/{len(jd_skills)} skills match - skill gap")
    
    final_score = max(0, min(100, base_score + notice_adjustment + interest_adjustment))
    
    return float(final_score), reasoning  # ← FIXED: Return float instead of int


def generate_candidate_explanation(row, match_score, matched_skills, missing_skills, interest_score, final_score):
    """Generate human-readable explanation for candidate ranking"""
    
    # Skill analysis
    skill_explanation = ""
    if len(matched_skills) > 0:
        skill_explanation = f"✅ **Strong Match**: Matched on {', '.join(matched_skills)}"
    if len(missing_skills) > 0:
        skill_explanation += f"\n⚠️ **Skill Gaps**: Missing {', '.join(missing_skills)}"
    
    # Interest analysis with reasoning tags
    interest_reason = ""
    default_interest = row.get("Default Interest", "medium")
    notice = row.get("Notice Period", "30 days")
    
    if default_interest == "high":
        interest_reason = "🔥 **High Interest Signal**: Candidate marked as actively looking"
    elif default_interest == "medium":
        interest_reason = "👍 **Moderate Interest Signal**: Candidate open to opportunities"
    else:
        interest_reason = "❓ **Low Interest Signal**: Candidate passively looking"
    
    # Notice period impact
    if "15" in str(notice) or "immediate" in str(notice).lower():
        interest_reason += "\n⏱️ **Quick Join**: Short notice period indicates availability"
    elif "60" in str(notice) or "90" in str(notice):
        interest_reason += "\n⚠️ **Long Notice**: May affect joining timeline"
    
    # Final recommendation
    if final_score >= 85:
        recommendation = "🎯 **Action**: Contact immediately - Top priority candidate"
    elif final_score >= 70:
        recommendation = "📞 **Action**: Schedule screening call this week"
    elif final_score >= 55:
        recommendation = "📋 **Action**: Keep in shortlist for now"
    elif final_score >= 40:
        recommendation = "🔄 **Action**: Consider as backup option"
    else:
        recommendation = "❌ **Action**: Remove from shortlist"
    
    return {
        "skill_analysis": skill_explanation,
        "interest_analysis": interest_reason,
        "recommendation": recommendation,
        "match_breakdown": {
            "matched": matched_skills,
            "missing": missing_skills,
            "match_percentage": match_score
        }
    }

# -------------------------------
# Main UI
# -------------------------------
st.set_page_config(page_title="AI Talent Scouting Agent", layout="wide")
# -------------------------------
# Custom CSS for Background Colors
# -------------------------------
st.markdown("""
<style>
    /* Main app background - Light yellow shade */
    .stApp {
        background-color: #FFFDF5;
    }
    
    /* Main content area background */
    .main {
        background-color: #FFFDF5;
    }
    
    /* Sidebar - Darker yellow/orange shade */
    [data-testid="stSidebar"] {
        background-color: #FEF9E6;
        border-right: 1px solid #F0E6C5;
    }
    
    /* Sidebar content styling */
    [data-testid="stSidebar"] .stMarkdown {
        color: #5D4E37;
    }
    
    /* Sidebar headers */
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #8B6914;
    }
    
    /* Card backgrounds */
    .stAlert, .stInfo, .stSuccess, .stWarning {
        background-color: #FFF8E7;
    }
    
    /* Expander headers */
    .streamlit-expanderHeader {
        background-color: #FFF8E7;
        border-radius: 8px;
    }
    
    /* Dataframe background */
    .stDataFrame {
        background-color: #FFFFFF;
    }
    
    /* Text area background */
    .stTextArea textarea {
        background-color: #FFFFFF;
        border: 1px solid #F0E6C5;
    }
    
    /* Button styling */
    .stButton button {
        background-color: #F5E6B8;
        border: 1px solid #E6D5A8;
    }
    
    .stButton button:hover {
        background-color: #EDD68E;
        border: 1px solid #D4C088;
    }
    
    /* Primary button */
    .stButton button[kind="primary"] {
        background-color: #E6C87A;
        border-color: #D4B66A;
    }
    
    /* Metric cards */
    .stMetric {
        background-color: #FFF8E7;
        border-radius: 10px;
        padding: 10px;
        border: 1px solid #F0E6C5;
    }
    
    /* Chat bubbles */
    .chat-agent {
        background: #F5E6B8;
        border-radius: 18px;
        padding: 10px 16px;
        max-width: 75%;
        margin: 8px 0;
    }
    
    /* Status containers */
    .stStatus {
        background-color: #FFF8E7;
    }
</style>
""", unsafe_allow_html=True)

st.title("💼 AI-Powered Talent Scouting & Engagement Agent")
st.markdown("---")

# Sidebar for instructions
with st.sidebar:
    st.markdown("### 📋 Instructions")
    st.markdown("""
    1. Paste a Job Description below
    2. Click 'Run Agent'
    3. Agent will:
       - Extract skills from JD
       - Match with candidates
       - Simulate interest
       - Rank candidates
    """)
    st.markdown("---")
    st.markdown("### 📊 Scoring Logic")
    st.markdown("""
    - **Match Score**: Skills match % (0-100)
    - **Interest Score**: Simulated candidate interest (0-100)
    - **Final Score**: (Match × 0.6) + (Interest × 0.4)
    """)
    st.markdown("---")
    st.markdown("### 🏆 Ranking Scale")
    st.markdown("""
    - **A+ (85-100)**: Excellent fit - Contact immediately
    - **A (70-84)**: Good fit - Schedule screening
    - **B (55-69)**: Moderate fit - Keep in shortlist
    - **C (40-54)**: Low fit - Consider as backup
    - **D (<40)**: Poor fit - Remove from list
    """)

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### Job Description Input")
    jd_input = st.text_area(
        "Paste the job description here:",
        height=200,
        placeholder="Example: Looking for a Senior Python Developer with 5+ years experience in Python, SQL, and Machine Learning..."
    )

with col2:
    st.markdown("### 🔧 Sample JD (Quick Test)")
    if st.button("📋 Load Sample JD"):
        sample_jd = """We are looking for a Data Scientist with:
        - 3+ years experience in Python and SQL
        - Strong Machine Learning background
        - Experience with NLP and Deep Learning
        - Knowledge of AWS is a plus"""
        jd_input = sample_jd
        st.rerun()

# Run button
run_button = st.button("Run Scouting", type="primary", use_container_width=True)

if run_button:
    if not jd_input.strip():
        st.warning("Please paste a job description first.")
        st.stop()
    
    # Check if candidates file exists
    if not os.path.exists(file_path):
        st.error("candidates.csv not found!")
        st.info("Please create a 'candidates.csv' file in the same folder")
        st.stop()
    
    with st.spinner("Processing..."):
        # Extract skills from JD
        jd_skills = extract_jd_info(jd_input)
        st.session_state['jd_skills'] = jd_skills
        
        # Load candidates
        df = pd.read_csv(file_path)
        st.session_state['df'] = df
        
        st.success(f"Loaded {len(df)} candidates")
        
        # Display extracted skills in a clean row
        st.markdown("**Skills detected:**")
        skill_badges = " ".join([f"<span style='background:#e9ecef; padding:4px 12px; border-radius:20px; font-size:0.8rem;'>{s}</span>" for s in jd_skills])
        st.markdown(skill_badges, unsafe_allow_html=True)
        st.markdown("---")
        
        # Process each candidate
        results = []
        progress_bar = st.progress(0)
        
        for idx, (_, row) in enumerate(df.iterrows()):
            # Calculate match score
            match_score, matched_skills, missing_skills = calculate_match_score(
                jd_skills, row["Key Skills"]
            )
            
            # Simulate interest
            response = simulate_candidate_response(row, jd_skills, jd_input)
            
            # Calculate interest score
            interest_score, reasoning_tags = get_interest_score_from_response(response, row, jd_skills)
            
            # Calculate final score
            final_score = calculate_final_score(match_score, interest_score, 0.6, 0.4)
            
            # Get ranking info
            rank_info = get_rank_description(final_score)
            
            # Store results
            results.append({
                "Name": row["Name"],
                "Current Role": row["Current Role"],
                "Experience": row.get("Experience (yrs)", "N/A"),
                "Location": row.get("Location", "N/A"),
                "Notice Period": row.get("Notice Period", "N/A"),
                "Match Score": match_score,
                "Interest Score": interest_score,
                "Final Score": round(final_score, 2),
                "Rank": rank_info["rank"],
                "Recommendation": rank_info["action"],
                "Matched Skills": ", ".join(matched_skills) if matched_skills else "None",
                "Missing Skills": ", ".join(missing_skills) if missing_skills else "None",
                "Candidate Response": response,
                "Reasoning Tags": reasoning_tags
            })
            
            progress_bar.progress((idx + 1) / len(df))
        
        progress_bar.empty()
        
        # Create DataFrame and sort
        results_df = pd.DataFrame(results)
        results_df = results_df.sort_values(by="Final Score", ascending=False)
        st.session_state['results_df'] = results_df
        
        # Display results
        st.markdown("## Ranked Shortlist")
        st.markdown(f"**Total candidates:** {len(results_df)}")
        
        # Top 3 highlight - Clean version with bigger text
        st.markdown("### Top Candidates")
        top3_cols = st.columns(3)

        # Different colors for each position
        box_colors = [
            {"bg": "#FFF8E7", "border": "#FFD700", "badge": "#FFA500"},  # Gold theme for #1
            {"bg": "#F0F4FF", "border": "#667eea", "badge": "#667eea"},  # Blue theme for #2
            {"bg": "#FFF0F0", "border": "#f093fb", "badge": "#f093fb"}   # Pink theme for #3
        ]
        
        medal_icons = ["🥇", "🥈", "🥉"]
        
        for i, (_, row) in enumerate(results_df.head(3).iterrows()):
            with top3_cols[i]:
                colors = box_colors[i]
                medal = medal_icons[i]
                
                # Set badge color based on rank
                if row['Rank'] == 'A+':
                    badge_bg = "#11998e"
                elif row['Rank'] == 'A':
                    badge_bg = "#667eea"
                else:
                    badge_bg = "#f093fb"
                    
                st.markdown(f"""
                <div style="background: {colors['bg']}; border-radius: 20px; padding: 20px; text-align: center; border: 2px solid {colors['border']}; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                    <div style="font-size: 2.2rem;">{medal}</div>
                    <div style="font-size: 1.3rem; font-weight: 700; margin: 8px 0;">{row['Name']}</div>
                    <div style="font-size: 0.85rem; color: #666; margin-bottom: 16px;">{row['Current Role']}</div>
                    <div style="margin: 16px 0;">
                        <span style="font-size: 2rem; font-weight: 800;">{row['Final Score']}</span>
                        <span style="color: #aaa;">/100</span>
                    </div>
                    <div style="display: flex; justify-content: center; gap: 24px;">
                        <div><strong style="font-size: 1.1rem;">{row['Match Score']:.0f}</strong><br><span style="font-size: 0.7rem; color: #666;">MATCH</span></div>
                        <div><strong style="font-size: 1.1rem;">{row['Interest Score']:.0f}</strong><br><span style="font-size: 0.7rem; color: #666;">INTEREST</span></div>
                    </div>
                    <div style="margin-top: 16px;">
                        <span style="background: {badge_bg}; color: white; padding: 4px 16px; border-radius: 20px; font-size: 0.75rem; font-weight: 600;">{row['Rank']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # Full table
        st.markdown("### 📊 Complete Ranking Table")
        
        # Format dataframe for display
        display_df = results_df.copy()
        display_cols = ["Name", "Current Role", "Final Score", "Match Score", 
                        "Interest Score", "Rank", "Recommendation", "Matched Skills", 
                        "Missing Skills", "Candidate Response"]
        display_df = display_df[[col for col in display_cols if col in display_df.columns]]
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Final Score": st.column_config.NumberColumn(format="%.2f"),
                "Match Score": st.column_config.NumberColumn(format="%.1f"),
                "Interest Score": st.column_config.NumberColumn(format="%.1f"),
            }
        )
        
        # Download button
        csv = results_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Results as CSV",
            data=csv,
            file_name="talent_scouting_results.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        st.markdown("---")
        st.success("✅ Done! Recruiters can now act on this ranked shortlist.")


# -------------------------------
# Conversational Outreach Simulation
# -------------------------------
st.markdown("---")
st.markdown("### 💬 Conversational Outreach Simulation")

# Check if results exist in session state
if 'results_df' in st.session_state and 'df' in st.session_state and 'jd_skills' in st.session_state:
    results_df = st.session_state['results_df']
    df = st.session_state['df']
    jd_skills = st.session_state['jd_skills']
    
    # Let user select which candidate to chat with
    conversation_candidate = st.selectbox(
        "Select a candidate:",
        options=results_df['Name'].tolist(),
        index=0,
        key="conversation_select"
    )
    
    # Get selected candidate details
    selected_row = results_df[results_df['Name'] == conversation_candidate].iloc[0]
    original_candidate = df[df['Name'] == conversation_candidate].iloc[0]
    
    # Generate conversation
    conversation = generate_conversation(original_candidate.to_dict(), jd_skills)
    
    # Calculate interest score from conversation
    conv_interest_score = calculate_interest_from_conversation(original_candidate.to_dict(), jd_skills)
    
    # Display conversation in chat format with light background
    st.markdown(f"#### Conversation with {conversation_candidate}")
    
    # Conversation container with light background
    st.markdown("""
    <div style="background: #F8F9FA; border-radius: 16px; padding: 20px; border: 1px solid #E9ECEF;">
    """, unsafe_allow_html=True)
    
    # Create chat display
    for msg in conversation:
        if msg["speaker"] == "agent":
            st.markdown(f"""
            <div style="display: flex; margin: 12px 0;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 10px 18px; border-radius: 20px; max-width: 80%;">
                    <b>Agent:</b> {msg['message']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="display: flex; justify-content: flex-end; margin: 12px 0;">
                <div style="background: #E8F4FD; color: #1a1a1a; padding: 10px 18px; border-radius: 20px; max-width: 80%;">
                    <b>{conversation_candidate}:</b> {msg['message']}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Show interest score from conversation
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Match Score", f"{selected_row['Match Score']:.0f}")
    
    with col2:
        st.metric("Interest Score", f"{conv_interest_score}")
    
    with col3:
        final_conv_score = calculate_final_score(selected_row['Match Score'], conv_interest_score, 0.6, 0.4)
        st.metric("Final Score", f"{final_conv_score:.0f}")
    
    # Get rank info for conversation
    conv_rank_info = get_rank_description(final_conv_score)
    st.markdown(f"**Rank:** {conv_rank_info['rank']} - {conv_rank_info['description']}")
    
    # Recommendation based on score
    if conv_interest_score >= 70:
        st.success("High interest candidate - Strongly recommend reaching out!")
    elif conv_interest_score >= 50:
        st.info("Moderate interest - Worth pursuing with more details")
    else:
        st.warning("Low interest - May need more convincing")
    
    # Add option to export conversation
    st.download_button(
        label="Export Conversation",
        data=str(conversation),
        file_name=f"conversation_{conversation_candidate}.txt",
        mime="text/plain",
        key="export_conversation"
    )
else:
    st.info("Run the scouting first to see conversations with candidates.")

# -------------------------------
# Recruiter Insights Hub
# -------------------------------

# Create a styled container for the entire section
st.markdown("""
<style>
.insights-hub {
    background: linear-gradient(135deg, #F0F9FF 0%, #E0F2FE 100%);
    border-radius: 24px;
    padding: 20px;
    margin: 20px 0;
    border: 1px solid #BAE6FD;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}
.insights-title {
    color: #0369A1;
    font-size: 1.5rem;
    font-weight: 700;
    margin-bottom: 0;
}
.insights-subtitle {
    color: #0C4A6E;
    font-size: 0.9rem;
    margin-bottom: 20px;
}
.insight-display {
    background: white;
    border-radius: 16px;
    padding: 20px;
    border: 1px solid #BAE6FD;
    margin-top: 15px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="insights-hub">', unsafe_allow_html=True)

st.markdown('<div class="insights-title">🎯 Recruiter Insights Hub</div>', unsafe_allow_html=True)
st.markdown('<div class="insights-subtitle">Get instant insights about candidates with one click</div>', unsafe_allow_html=True)

if 'results_df' in st.session_state and len(st.session_state['results_df']) > 0:
    results_df = st.session_state['results_df']
    jd_skills = st.session_state.get('jd_skills', [])
    
    # Get top candidates
    top1 = results_df.iloc[0].to_dict()
    top2 = results_df.iloc[1].to_dict() if len(results_df) > 1 else None
    top3 = results_df.iloc[2].to_dict() if len(results_df) > 2 else None
    
    # Function to generate insights
    def get_insight(insight_type):
        if insight_type == "whom_to_hire":
            best = top1
            second = top2
            reason = ""
            if best['Rank'] == 'A+':
                reason = f"{best['Name']} is an **excellent fit** with {best['Final Score']}% score"
            elif best['Rank'] == 'A':
                reason = f"{best['Name']} is a **strong candidate** with {best['Final Score']}% score"
            else:
                reason = f"{best['Name']} is the **best available** with {best['Final Score']}% score"
            
            return f"""
**🎯 Recommendation: Hire {best['Name']}**

{reason}

**Why {best['Name']}?**
• Match Score: {best['Match Score']}%
• Interest Score: {best['Interest Score']}%
• Matched Skills: {best['Matched Skills']}

**Backup:** {second['Name'] if second else 'None'} ({second['Final Score'] if second else 0}%)
"""
        
        elif insight_type == "top_candidates":
            return f"""
**🏆 Top 3 Candidates**

**1. {top1['Name']}** - {top1['Final Score']}%
• Match: {top1['Match Score']}% | Interest: {top1['Interest Score']}%
• Skills: {top1['Matched Skills']}

**2. {top2['Name']}** - {top2['Final Score']}%
• Match: {top2['Match Score']}% | Interest: {top2['Interest Score']}%
• Skills: {top2['Matched Skills']}

**3. {top3['Name']}** - {top3['Final Score']}%
• Match: {top3['Match Score']}% | Interest: {top3['Interest Score']}%
• Skills: {top3['Matched Skills']}
"""
        
        elif insight_type == "skill_gaps":
            missing = top1['Missing Skills']
            return f"""
**📊 Skill Gap Analysis for {top1['Name']}**

**Match Score:** {top1['Match Score']}%

**Missing Skills:** {missing}

**Recommendation:** Focus on upskilling in {missing.split(',')[0] if missing != 'None' else 'key areas'} to improve fit.
"""
        
        elif insight_type == "outreach_email":
            return f"""
**📧 Outreach Email for {top1['Name']}**

**Subject:** Exciting Opportunity: {top1['Current Role']} Role

Hi {top1['Name']},

I came across your profile and was impressed by your experience.

Your profile shows a **{top1['Match Score']}% match** with our requirements. We're looking for someone with skills in {', '.join(jd_skills[:3])}.

Would you be available for a quick 15-minute chat this week?

Looking forward to hearing from you!

Best regards,
TalentScout AI Recruitment Team
"""
        
        elif insight_type == "compare_top2" and top2:
            winner = top1 if top1['Final Score'] > top2['Final Score'] else top2
            return f"""
**⚖️ Comparison: {top1['Name']} vs {top2['Name']}**

| Metric | {top1['Name']} | {top2['Name']} |
|--------|---------------|---------------|
| Match Score | {top1['Match Score']}% | {top2['Match Score']}% |
| Interest Score | {top1['Interest Score']}% | {top2['Interest Score']}% |
| Final Score | {top1['Final Score']}% | {top2['Final Score']}% |
| Rank | {top1['Rank']} | {top2['Rank']} |

**🏆 Winner:** {winner['Name']} with {winner['Final Score']}%
"""
        
        elif insight_type == "jd_summary":
            return f"""
**📋 Job Description Summary**

**Required Skills:** {', '.join(jd_skills)}

**Top Candidate:** {top1['Name']} ({top1['Final Score']}% match)

**Average Match:** {results_df['Match Score'].mean():.1f}%

**Total Candidates:** {len(results_df)}

**Recommendation:** Focus on candidates with 70%+ match for immediate interviews.
"""
        
        return "Click any button above to get insights"
    
    # Quick Insights Buttons
    st.markdown("**Quick Insights**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🏆 Whom to Hire?", use_container_width=True, key="insight_hire"):
            insight = get_insight("whom_to_hire")
            st.session_state['current_insight'] = insight
            st.rerun()
        
        if st.button("📧 Outreach Email", use_container_width=True, key="insight_email"):
            insight = get_insight("outreach_email")
            st.session_state['current_insight'] = insight
            st.rerun()
    
    with col2:
        if st.button("📊 Top Candidates", use_container_width=True, key="insight_top"):
            insight = get_insight("top_candidates")
            st.session_state['current_insight'] = insight
            st.rerun()
        
        if st.button("⚖️ Compare Top 2", use_container_width=True, key="insight_compare"):
            insight = get_insight("compare_top2") if top2 else "Need at least 2 candidates to compare"
            st.session_state['current_insight'] = insight
            st.rerun()
    
    with col3:
        if st.button("📊 Skill Gaps", use_container_width=True, key="insight_gaps"):
            insight = get_insight("skill_gaps")
            st.session_state['current_insight'] = insight
            st.rerun()
        
        if st.button("📋 JD Summary", use_container_width=True, key="insight_jd"):
            insight = get_insight("jd_summary")
            st.session_state['current_insight'] = insight
            st.rerun()
    
    # Display current insight
    if 'current_insight' in st.session_state and st.session_state['current_insight']:
        st.markdown('<div class="insight-display">', unsafe_allow_html=True)
        st.markdown(st.session_state['current_insight'])
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Clear button
        if st.button("🗑️ Clear Insight", use_container_width=True, key="clear_insight"):
            st.session_state['current_insight'] = ""
            st.rerun()
    else:
        st.markdown('<div class="insight-display" style="text-align: center; color: #6B7280;">🔍 Click any button above to get insights about candidates</div>', unsafe_allow_html=True)

else:
    st.info("👆 Run the scouting first to get recruiter insights")

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("🔧 **AI-Powered Talent Scouting Agent** | Match Score (60%) + Interest Score (40%) = Final Rank")
