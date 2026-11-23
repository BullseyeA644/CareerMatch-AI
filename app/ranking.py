
import re

SENIOR_ROLES = {
    "senior", "staff", "principal",
    "lead", "director", "manager",
    "architect", "head"
}

NON_TECH_ROLES = {
    "business development",
    "customer success",
    "sales",
    "marketing",
    "recruiter"
}



import re

SENIOR_ROLES = {
    "senior", "sr", "staff", "principal",
    "lead", "director", "manager",
    "architect", "head", "chief"
}

NON_TECH_ROLES = {
    "business development",
    "customer success",
    "sales",
    "marketing",
    "recruiter",
    "physician",
    "nurse",
    "clinical",
    "tax",
    "human resources"
}

TECH_ROLES = {
    "software",
    "developer",
    "backend",
    "frontend",
    "full stack",
    "fullstack",
    "machine learning",
    "deep learning",
    "data scientist",
    "data science",
    "data engineer",
    "data analyst",
    "python",
    "artificial intelligence",
    "computer vision",
    "nlp",
    "devops",
    "mlops",
    "applied scientist"
}


def eligible_for_student(job):
    title = str(job.get("title") or "").lower()
    words = set(re.findall(r"[a-z]+", title))

    # Reject senior positions
    if words.intersection(SENIOR_ROLES):
        return False

    # Reject unrelated positions
    if any(role in title for role in NON_TECH_ROLES):
        return False

    # Require a relevant technical role
    if not (
        any(role in title for role in TECH_ROLES)
        or re.search(r"\b(ai|ml|sde)\b", title)
    ):
        return False

    return True

