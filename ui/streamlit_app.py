import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )
)

import streamlit as st
import requests

from app.resume_parser import (
    extract_text_from_pdf
)

# =========================================
# Page Config
# =========================================

st.set_page_config(
    page_title="CareerMatch AI",
    page_icon="🚀",
    layout="wide"
)

from pathlib import Path

from app.scraper import scrape_all_jobs
from app.rag_pipeline import (
    load_jobs,
    retrieve_jobs,
    vector_db
)

# Load Groq key from Streamlit Cloud secrets
if not os.getenv("GROQ_API_KEY"):
    try:
        os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
    except (FileNotFoundError, KeyError):
        pass

from app.llm_reasoning import generate_reasoning


@st.cache_resource(show_spinner="Preparing job database...")
def prepare_database():

    data_file = Path("data/jobs.json")

    if not data_file.exists():
        scrape_all_jobs()

    if not data_file.exists():
        raise RuntimeError("Unable to fetch job listings.")

    load_jobs()

    return True


# =========================================
# Custom CSS
# =========================================

st.markdown("""
<style>

.stApp {
    background-color: #0f172a;
    color: white;
}

.job-container {
    background-color: #1e293b;
    padding: 25px;
    border-radius: 15px;
    margin-bottom: 25px;
    border: 1px solid #334155;
}

.skill-badge {
    display: inline-block;
    padding: 6px 12px;
    margin-right: 8px;
    margin-top: 8px;
    border-radius: 20px;
    background-color: #2563eb;
    color: white;
    font-size: 14px;
}

.apply-btn {
    display: inline-block;
    padding: 10px 18px;
    border-radius: 10px;
    background-color: #22c55e;
    color: white !important;
    text-decoration: none;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)

# =========================================
# Header
# =========================================

st.title("🚀 CareerMatch AI")

st.write(
    "AI-Powered Semantic Resume Matching Platform"
)

st.markdown("---")

# =========================================
# Upload Resume
# =========================================

uploaded_file = st.file_uploader(
    "📄 Upload Resume PDF",
    type=["pdf"]
)

resume_text = ""

# =========================================
# Extract Resume Text
# =========================================

if uploaded_file is not None:

    with st.spinner(
        "Extracting resume..."
    ):

        resume_text = extract_text_from_pdf(
            uploaded_file
        )

    st.success(
        "Resume uploaded successfully!"
    )

    with st.expander(
        "📃 View Extracted Resume Text"
    ):

        st.text(
            resume_text[:5000]
        )

# =========================================
# Match Jobs
# =========================================


# =========================================
# Location Preference
# =========================================

st.subheader("Job Location Preference")

location_option = st.selectbox(
    "Where do you want to work?",
    [
        "India Eligible (Remote)",
        "Worldwide"
    ]
)

location_preference = (
    "india"
    if location_option == "India Eligible (Remote)"
    else "worldwide"
)


if st.button("🔍 Match Jobs"):

    if resume_text.strip() == "":

        st.warning(
            "Please upload a PDF resume."
        )

    else:

        try:

            with st.spinner(
                "Finding best jobs..."
            ):


                prepare_database()

                results = retrieve_jobs(
                    resume_text,
                    location_preference=location_preference
                )

                matches = []

                for item in results:
                    job = item["job"]

                    reasoning = generate_reasoning(
                        resume_text,
                        job
                    )

                    matches.append({
                        "job_title": job.get("title", "N/A"),
                        "company": job.get("company", "N/A"),
                        "location": job.get("location", "Remote"),
                        "source": job.get("source", "Unknown"),
                        "job_url": job.get("url", ""),
                        "match_percentage": round(float(item["score"]), 2),
                        "reasoning": reasoning or "Analysis unavailable."
                    })

                data = {
                    "success": True,
                    "total_matches": len(matches),
                    "matches": matches
                }


                if data["success"]:

                    st.subheader(
                        "🎯 Top Matching Jobs"
                    )

                    for match in data["matches"]:

                        # =====================================
                        # Skill Extraction
                        # =====================================

                        skills = []

                        reasoning = (
                            match["reasoning"]
                        ).lower()

                        tech_keywords = [
                            "python",
                            "fastapi",
                            "machine learning",
                            "tensorflow",
                            "pytorch",
                            "react",
                            "sql",
                            "nlp",
                            "openai",
                            "langchain"
                        ]

                        for tech in tech_keywords:

                            if tech in reasoning:

                                skills.append(
                                    tech.title()
                                )

                        # =====================================
                        # Job Card
                        # =====================================

                        with st.container():

                            st.markdown(
                                '<div class="job-container">',
                                unsafe_allow_html=True
                            )

                            st.subheader(
                                match["job_title"]
                            )

                            st.write(
                                f"🏢 Company: {match['company']}"
                            )

                            st.write(
                                f"🎯 Match Score: {match['match_percentage']}%"
                            )

                            # Progress bar
                            st.progress(
                                int(
                                    match[
                                        "match_percentage"
                                    ]
                                )
                            )

                            # Skill badges
                            badge_html = ""

                            for skill in skills:

                                badge_html += f"""
                                <span class="skill-badge">
                                    {skill}
                                </span>
                                """

                            st.markdown(
                                badge_html,
                                unsafe_allow_html=True
                            )

                            st.write("")

                            # AI reasoning
                            with st.expander(
                                "🧠 View AI Analysis"
                            ):

                                st.write(
                                    match["reasoning"]
                                )

                                st.write(
                                    f"📍 Location: {match['location']}"
                                )

                                st.write(
                                    f"🌐 Source: {match['source']}"
                                )

                            # Apply button
                            if match["job_url"]:

                                st.markdown(
                                    f"""
                                    <a href="{match['job_url']}"
                                    target="_blank"
                                    class="apply-btn">
                                    Apply Now
                                    </a>
                                    """,
                                    unsafe_allow_html=True
                                )

                            st.markdown(
                                "</div>",
                                unsafe_allow_html=True
                            )

                            st.markdown("---")

                else:

                    st.error(
                        data["error"]
                    )

        except Exception as e:

            st.error(
                f"Connection Error: {str(e)}"
            )