
import requests
import json
import html
import re
from pathlib import Path


def clean_description(value):
    text = html.unescape(str(value or ""))
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()[:2500]


def fetch_remoteok_jobs():
    print("Fetching RemoteOK jobs...")

    try:
        response = requests.get(
            "https://remoteok.com/api",
            headers={"User-Agent": "CareerMatchAI/1.0"},
            timeout=20
        )
        response.raise_for_status()

        jobs = []

        for item in response.json():
            if not isinstance(item, dict):
                continue
            if not item.get("position"):
                continue

            jobs.append({
                "title": item.get("position") or "",
                "company": item.get("company") or "",
                "description": clean_description(
                    item.get("description")
                ),
                "location": item.get("location") or "Remote",
                "source": "RemoteOK",
                "url": item.get("url") or ""
            })

        return jobs

    except (requests.RequestException, ValueError) as e:
        print("RemoteOK error:", e)
        return []


def fetch_arbeitnow_jobs():
    print("Fetching Arbeitnow jobs...")

    try:
        response = requests.get(
            "https://www.arbeitnow.com/api/job-board-api",
            timeout=30
        )
        response.raise_for_status()

        jobs = []

        for item in response.json().get("data", []):
            jobs.append({
                "title": item.get("title") or "",
                "company": item.get("company_name") or "",
                "description": clean_description(
                    item.get("description")
                ),
                "location": item.get("location") or "",
                "source": "Arbeitnow",
                "url": item.get("url") or ""
            })

        return jobs

    except (requests.RequestException, ValueError) as e:
        print("Arbeitnow error:", e)
        return []


def fetch_himalayas_jobs():
    print("Fetching India-eligible jobs from Himalayas...")

    from time import time

    queries = [
        "software",
        "python",
        "machine learning",
        "data engineer"
    ]

    jobs = []
    seen = set()

    for query in queries:
        try:
            response = requests.get(
                "https://himalayas.app/jobs/api/search",
                params={
                    "country": "IN",
                    "q": query,
                    "sort": "recent",
                    "page": 1
                },
                timeout=30
            )

            response.raise_for_status()
            data = response.json()

            for item in data.get("jobs", []):
                guid = item.get("guid")

                if guid and guid in seen:
                    continue

                expiry = item.get("expiryDate")
                if expiry is not None and float(expiry) <= time():
                    continue

                application_url = item.get("applicationLink")
                if not application_url:
                    continue

                job = {
                    "title": item.get("title") or "",
                    "company": item.get("companyName") or "",
                    "description": clean_description(
                        item.get("description") or item.get("excerpt")
                    ),
                    "location": "Remote - India eligible",
                    "source": "Himalayas",
                    "source_url": "https://himalayas.app",
                    "url": application_url,
                    "employment_type": item.get("employmentType") or "",
                    "seniority": item.get("seniority") or "",
                    "location_restrictions": item.get("locationRestrictions") or [],
                    "expires_at": expiry,
                    "guid": guid
                }

                jobs.append(job)

                if guid:
                    seen.add(guid)

        except (requests.RequestException, ValueError, TypeError) as e:
            print(f"Himalayas error for {query}: {e}")

    print(f"Fetched {len(jobs)} Himalayas jobs")
    return jobs

def clean_jobs(jobs):
    cleaned = []
    seen = set()

    for job in jobs:
        title = str(job.get("title") or "")
        description = str(job.get("description") or "")

        if len(title) < 3 or len(description) < 20:
            continue

        identity = (
            title.strip().lower(),
            str(job.get("company") or "").strip().lower()
        )

        if identity in seen:
            continue

        seen.add(identity)
        cleaned.append(job)

    return cleaned


def save_jobs(jobs):
    Path("data").mkdir(exist_ok=True)

    with open("data/jobs.json", "w", encoding="utf-8") as f:
        json.dump(jobs, f, indent=2, ensure_ascii=False)



def scrape_all_jobs():
    data_path = Path("data/jobs.json")

    previous_jobs = []

    if data_path.exists():
        try:
            previous_jobs = json.loads(
                data_path.read_text(encoding="utf-8")
            )
        except (OSError, ValueError):
            previous_jobs = []

    sources = [
        ("RemoteOK", fetch_remoteok_jobs()),
        ("Arbeitnow", fetch_arbeitnow_jobs()),
        ("Himalayas", fetch_himalayas_jobs())
    ]

    all_jobs = []

    for source, new_jobs in sources:
        print(f"{source}: {len(new_jobs)} fetched")

        if new_jobs:
            all_jobs.extend(new_jobs)
        else:
            saved_jobs = [
                job for job in previous_jobs
                if job.get("source") == source
            ]

            print(
                f"Retaining {len(saved_jobs)} "
                f"previous {source} jobs"
            )

            all_jobs.extend(saved_jobs)

    cleaned_jobs = clean_jobs(all_jobs)

    if cleaned_jobs:
        save_jobs(cleaned_jobs)
        print(f"Saved {len(cleaned_jobs)} jobs")
        return cleaned_jobs

    print("No valid jobs. Dataset unchanged.")
    return previous_jobs

