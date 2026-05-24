"""
ResuMatch AI — Job Aggregator
Fetches and normalizes job listings from multiple public APIs.
Sources: RemoteOK, Jobicy, Arbeitnow, Himalayas
"""

import asyncio
import hashlib
import time
import re
from datetime import datetime
from typing import Optional

import httpx

# Cache for job results
_job_cache: dict = {"data": [], "timestamp": 0, "ttl": 1800}  # 30 min TTL

# Common headers to avoid rate limiting
HEADERS = {
    "User-Agent": "ResuMatch-AI/1.0 (resume-job-matcher; contact@resumatch.dev)",
    "Accept": "application/json",
}

REQUEST_TIMEOUT = 8.0  # seconds per source


def _strip_html(html: str) -> str:
    """Strip HTML tags from a string."""
    if not html:
        return ""
    clean = re.sub(r"<[^>]+>", " ", html)
    clean = re.sub(r"\s+", " ", clean)
    return clean.strip()[:5000]  # Limit to 5K chars


def _generate_id(source: str, title: str, company: str) -> str:
    """Generate a deterministic ID for deduplication."""
    key = f"{source}:{title}:{company}".lower()
    return hashlib.md5(key.encode()).hexdigest()[:12]


async def _fetch_remoteok(client: httpx.AsyncClient) -> list[dict]:
    """Fetch jobs from RemoteOK API."""
    try:
        resp = await client.get(
            "https://remoteok.com/api",
            headers={**HEADERS, "User-Agent": "ResuMatch-AI/1.0"},
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        
        # First element is meta, skip it
        jobs_raw = data[1:] if len(data) > 1 else []
        
        jobs = []
        for j in jobs_raw[:50]:
            jobs.append({
                "id": _generate_id("remoteok", j.get("position", ""), j.get("company", "")),
                "title": j.get("position", "Unknown"),
                "company": j.get("company", "Unknown"),
                "description": _strip_html(j.get("description", "")),
                "tags": j.get("tags", []),
                "location": j.get("location", "Remote"),
                "salary_min": _parse_salary(j.get("salary_min")),
                "salary_max": _parse_salary(j.get("salary_max")),
                "url": j.get("apply_url") or j.get("url", ""),
                "source": "RemoteOK",
                "posted_at": j.get("date", ""),
                "company_logo": j.get("company_logo", ""),
            })
        
        return jobs
    except Exception as e:
        print(f"[RemoteOK] Error: {e}")
        return []


async def _fetch_jobicy(client: httpx.AsyncClient) -> list[dict]:
    """Fetch jobs from Jobicy API."""
    try:
        resp = await client.get(
            "https://jobicy.com/api/v2/remote-jobs",
            params={"count": 50},
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        
        jobs_raw = data.get("jobs", [])
        jobs = []
        for j in jobs_raw:
            jobs.append({
                "id": _generate_id("jobicy", j.get("jobTitle", ""), j.get("companyName", "")),
                "title": j.get("jobTitle", "Unknown"),
                "company": j.get("companyName", "Unknown"),
                "description": _strip_html(j.get("jobDescription", j.get("jobExcerpt", ""))),
                "tags": [j.get("jobIndustry", "")] if j.get("jobIndustry") else [],
                "location": j.get("jobGeo", "Remote"),
                "salary_min": _parse_salary(j.get("annualSalaryMin", j.get("salaryMin"))),
                "salary_max": _parse_salary(j.get("annualSalaryMax", j.get("salaryMax"))),
                "url": j.get("url", ""),
                "source": "Jobicy",
                "posted_at": j.get("pubDate", ""),
                "company_logo": j.get("companyLogo", ""),
            })
        
        return jobs
    except Exception as e:
        print(f"[Jobicy] Error: {e}")
        return []


async def _fetch_arbeitnow(client: httpx.AsyncClient) -> list[dict]:
    """Fetch jobs from Arbeitnow API."""
    try:
        resp = await client.get(
            "https://www.arbeitnow.com/api/job-board-api",
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        
        jobs_raw = data.get("data", [])
        jobs = []
        for j in jobs_raw[:50]:
            jobs.append({
                "id": _generate_id("arbeitnow", j.get("title", ""), j.get("company_name", "")),
                "title": j.get("title", "Unknown"),
                "company": j.get("company_name", "Unknown"),
                "description": _strip_html(j.get("description", "")),
                "tags": j.get("tags", []),
                "location": j.get("location", "Remote"),
                "salary_min": None,
                "salary_max": None,
                "url": j.get("url", ""),
                "source": "Arbeitnow",
                "posted_at": _timestamp_to_iso(j.get("created_at")),
                "company_logo": "",
            })
        
        return jobs
    except Exception as e:
        print(f"[Arbeitnow] Error: {e}")
        return []


async def _fetch_himalayas(client: httpx.AsyncClient) -> list[dict]:
    """Fetch jobs from Himalayas API."""
    try:
        resp = await client.get(
            "https://himalayas.app/jobs/api",
            params={"limit": 20},
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        
        jobs_raw = data.get("jobs", [])
        jobs = []
        for j in jobs_raw:
            categories = j.get("categories", []) or j.get("category", [])
            if isinstance(categories, str):
                categories = [categories]
            
            jobs.append({
                "id": _generate_id("himalayas", j.get("title", ""), j.get("companyName", "")),
                "title": j.get("title", "Unknown"),
                "company": j.get("companyName", "Unknown"),
                "description": _strip_html(j.get("description", j.get("excerpt", ""))),
                "tags": categories,
                "location": "Remote",
                "salary_min": _parse_salary(j.get("minSalary")),
                "salary_max": _parse_salary(j.get("maxSalary")),
                "url": j.get("applicationLink", ""),
                "source": "Himalayas",
                "posted_at": j.get("pubDate", ""),
                "company_logo": j.get("companyLogo", ""),
            })
        
        return jobs
    except Exception as e:
        print(f"[Himalayas] Error: {e}")
        return []


def _parse_salary(value) -> Optional[int]:
    """Safely parse a salary value to integer."""
    if value is None:
        return None
    try:
        val = int(float(str(value).replace(",", "").replace("$", "").strip()))
        return val if 1000 < val < 10_000_000 else None
    except (ValueError, TypeError):
        return None


def _timestamp_to_iso(ts) -> str:
    """Convert Unix timestamp to ISO string."""
    if ts is None:
        return ""
    try:
        return datetime.fromtimestamp(int(ts)).isoformat()
    except (ValueError, TypeError, OSError):
        return str(ts)


async def aggregate_jobs(force_refresh: bool = False) -> dict:
    """
    Fetch and merge jobs from all sources.
    Results are cached for 30 minutes.
    
    Returns:
        {
            "jobs": [normalized job dicts],
            "sources": {"RemoteOK": int, "Jobicy": int, ...},
            "total": int,
            "cached": bool
        }
    """
    global _job_cache
    
    # Return cache if valid
    now = time.time()
    if not force_refresh and _job_cache["data"] and (now - _job_cache["timestamp"]) < _job_cache["ttl"]:
        return {
            "jobs": _job_cache["data"],
            "sources": _count_sources(_job_cache["data"]),
            "total": len(_job_cache["data"]),
            "cached": True,
        }
    
    # Fetch from all sources concurrently
    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(
            _fetch_remoteok(client),
            _fetch_jobicy(client),
            _fetch_arbeitnow(client),
            _fetch_himalayas(client),
            return_exceptions=True,
        )
    
    # Merge results
    all_jobs = []
    for result in results:
        if isinstance(result, list):
            all_jobs.extend(result)
        elif isinstance(result, Exception):
            print(f"[Aggregator] Source failed: {result}")
    
    # Deduplicate by ID
    seen = set()
    unique_jobs = []
    for job in all_jobs:
        if job["id"] not in seen:
            seen.add(job["id"])
            unique_jobs.append(job)
    
    # Update cache
    _job_cache["data"] = unique_jobs
    _job_cache["timestamp"] = now
    
    return {
        "jobs": unique_jobs,
        "sources": _count_sources(unique_jobs),
        "total": len(unique_jobs),
        "cached": False,
    }


def _count_sources(jobs: list[dict]) -> dict:
    """Count jobs per source."""
    counts = {}
    for job in jobs:
        source = job.get("source", "Unknown")
        counts[source] = counts.get(source, 0) + 1
    return counts


def clear_cache():
    """Clear the job cache."""
    global _job_cache
    _job_cache = {"data": [], "timestamp": 0, "ttl": 1800}
