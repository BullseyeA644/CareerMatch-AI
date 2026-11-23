# from openai import OpenAI

# from app.config import OPENAI_API_KEY

# # =========================================
# # OpenAI Client
# # =========================================

# client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = (
    OpenAI(
        api_key=GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1"
    )
    if GROQ_API_KEY
    else None
)


# =========================================
# Generate AI Reasoning
# =========================================

def generate_reasoning(
    resume,
    job
):
    if client is None:
        return (
            "AI explanation unavailable. "
            "Job matching is performed using semantic similarity."
        )

    try:

        prompt = f"""
        You are an expert AI recruiter and hiring assistant.

        Analyze the candidate resume
        against the retrieved job role.

        ============================
        CANDIDATE RESUME
        ============================

        {resume[:3000]}

        ============================
        JOB DETAILS
        ============================

        Job Title:
        {job.get('title', '')}

        Company:
        {job.get('company', '')}

        Location:
        {job.get('location', '')}

        ============================
        JOB DESCRIPTION
        ============================

        {job.get('description', '')[:2500]}

        ============================
        TASK
        ============================

        Explain:

        1. Why the candidate matches this role
        2. Relevant technical skills
        3. Relevant tools/frameworks
        4. Experience/project alignment
        5. Overall suitability

        RULES:
        - Keep response concise
        - Keep response professional
        - Use recruiter-style language
        - Maximum 120 words
        - Avoid bullet points
        """

        response = client.chat.completions.create(

            model="openai/gpt-oss-20b",

            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional AI hiring assistant."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.4,

            max_tokens=600
        )

        reasoning = (
            response
            .choices[0]
            .message
            .content
        )

        return reasoning

    except Exception as e:

        return (
            f"AI reasoning error: {str(e)}"
        )