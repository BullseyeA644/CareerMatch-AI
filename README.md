# CareerMatch AI

AI-Powered Resume Analysis and Job Recommendation System

## Overview

CareerMatch AI is a resume-based job recommendation platform that uses semantic search and large language models to identify relevant job opportunities.

The system extracts resume information, compares candidate profiles with job descriptions, and generates AI-powered explanations for job recommendations.

## Tech Stack

- Python
- FastAPI
- Streamlit
- Sentence Transformers
- FAISS
- Groq LLM API
- NumPy
- Backend: Python, FastAPI
- Frontend: Streamlit
- Embeddings: Sentence Transformers (all-MiniLM-L6-v2)
- Vector Search: FAISS
- LLM: GPT-OSS-20B via GroqCloud
- Data Sources: RemoteOK, Arbeitnow, Himalayas

## Features

- PDF resume upload and text extraction
- Semantic resume-to-job matching
- Vector similarity search using FAISS
- Automated job retrieval from RemoteOK
- Similarity-based job ranking
- LLM-generated job match explanations
- Interactive Streamlit dashboard

## System Workflow

1. Upload a resume.
2. Extract resume text.
3. Generate semantic embeddings.
4. Search job embeddings using FAISS.
5. Rank matching job opportunities.
6. Generate explanations through Groq LLM.
7. Display results in Streamlit.

## Run Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```env
GROQ_API_KEY=your_api_key
```

Start the backend:

```bash
python -m uvicorn app.main:app
```

Start the frontend in another terminal:

```bash
python -m streamlit run ui/streamlit_app.py
```

## Recent Improvements

- Integrated Groq LLM for AI-generated job match explanations
- Added job collection from RemoteOK, Arbeitnow, and Himalayas
- Implemented experience-aware and technical-role filtering
- Added India-eligible remote and Worldwide search preferences
- Expanded FAISS indexing to support the complete job dataset
- Added automatic dataset initialization on first startup
- Improved API response handling and numerical score formatting
