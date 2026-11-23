import json

from app.embeddings import get_embedding
from app.vector_store import VectorStore
from app.ranking import eligible_for_student

# =========================================
# Vector Database
# =========================================

vector_db = VectorStore()

# =========================================
# Build/Rebuild FAISS
# =========================================

def load_jobs():

    print("Loading jobs into FAISS...")

    # Reset FAISS
    vector_db.reset()

    with open(
        "data/jobs.json",
        "r",
        encoding="utf-8"
    ) as file:

        jobs = json.load(file)

    embeddings = []

    metadata = []



    for job in jobs:

        combined_text = f"""
        {job['title']}
        {job['description']}
        """

        embedding = get_embedding(
            combined_text
        )

        embeddings.append(
            embedding
        )

        metadata.append(job)

    vector_db.add_embeddings(
        embeddings,
        metadata
    )

    print(
        f"FAISS rebuilt with {len(jobs)} jobs"
    )

# =========================================
# Retrieve Jobs
# =========================================

def retrieve_jobs(resume_text, location_preference="worldwide"):

    resume_embedding = get_embedding(resume_text)

    total_jobs = vector_db.index.ntotal

    if total_jobs == 0:
        return []

    # Retrieve more candidates before filtering
    results = vector_db.search(
        resume_embedding,
        top_k=total_jobs
    )

    # Exclude senior and unrelated roles
    eligible_results = [
        item for item in results
        if eligible_for_student(item["job"])
    ]

    # Return the top 5 eligible matches
    if location_preference == "india":
        eligible_results = [
            item for item in eligible_results
            if item["job"].get("source") == "Himalayas"
            and item["job"].get("location") == "Remote - India eligible"
        ]

    return eligible_results[:5]
