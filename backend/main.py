"""
ResuMatch AI -- FastAPI Main Application
Endpoints for resume analysis, job discovery, auth, admin, interview prep, and resume rewriting.
"""

import json
import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, UploadFile, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from memory_manager import cleanup, memory_guard, get_memory_usage_mb, get_system_info
from parser import extract_text_from_pdf
from skill_extractor import extract_skills, get_skill_demand
from ats_scorer import calculate_ghost_score
from job_aggregator import aggregate_jobs
from matcher import model_exists
from database import init_db, log_analysis
from auth import router as auth_router, get_current_user, get_optional_user
from admin_routes import router as admin_router
from interview_generator import generate_interview_questions
from resume_rewriter import rewrite_resume


# ──────────────────────────────────────────────
# Lifespan: pre-load models on startup
# ──────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[Startup] ResuMatch AI initializing...")
    print(f"[Startup] Memory: {get_memory_usage_mb():.1f} MB")

    # Initialize database
    try:
        init_db()
    except Exception as e:
        print(f"[Startup] DB init warning: {e}")

    # Pre-load spaCy model
    try:
        from skill_extractor import _get_nlp
        _get_nlp()
        print("[Startup] spaCy model loaded [OK]")
    except Exception as e:
        print(f"[Startup] spaCy load warning: {e}")

    if model_exists():
        print("[Startup] ONNX model file found [OK]")
    else:
        print("[Startup] WARNING: ONNX model not found. Semantic matching unavailable.")

    career_path = os.path.join(os.path.dirname(__file__), "data", "career_paths.json")
    if os.path.exists(career_path):
        print("[Startup] Career paths data found [OK]")

    print(f"[Startup] Ready! Memory: {get_memory_usage_mb():.1f} MB")
    yield
    print("[Shutdown] Cleaning up...")
    cleanup()


# ──────────────────────────────────────────────
# App initialization
# ──────────────────────────────────────────────
app = FastAPI(
    title="ResuMatch AI",
    description="Zero-cost, API-free resume optimization & job matching",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router)
app.include_router(admin_router)


# ──────────────────────────────────────────────
# Health
# ──────────────────────────────────────────────
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "2.0.0",
        "memory": get_system_info(),
        "onnx_model_available": model_exists(),
        "timestamp": time.time(),
    }


# ──────────────────────────────────────────────
# Resume Analysis (auth required)
# ──────────────────────────────────────────────
@app.post("/analyze-resume")
async def analyze_resume(
    file: UploadFile = File(...),
    target_keywords: str = Query(default="", description="Comma-separated target job keywords"),
    user: dict = Depends(get_current_user),
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")
    if file.size and file.size > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size must be under 10MB")

    start_time = time.time()

    with memory_guard("resume_analysis"):
        try:
            pdf_bytes = await file.read()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to read file: {str(e)}")

        try:
            parsed = extract_text_from_pdf(pdf_bytes)
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"Failed to parse PDF: {str(e)}")

        if not parsed["text"] or len(parsed["text"].strip()) < 50:
            raise HTTPException(status_code=422, detail="Could not extract meaningful text from this PDF.")

        try:
            skills_data = extract_skills(parsed["text"])
        except Exception as e:
            skills_data = {"skills": [], "total_years": None, "skill_locations": {}}

        target_kw_list = [k.strip() for k in target_keywords.split(",") if k.strip()] if target_keywords else None
        try:
            ats_score = calculate_ghost_score(parsed, skills_data, target_kw_list)
        except Exception as e:
            ats_score = {"total_score": 0, "grade": "N/A", "breakdown": {}, "recommendations": []}

        career_paths = _get_career_recommendations(skills_data)

        for skill in skills_data.get("skills", []):
            skill["demand"] = get_skill_demand(skill["name"])

        matched_jobs = []
        if model_exists():
            try:
                job_data = await aggregate_jobs()
                if job_data["jobs"]:
                    from matcher import match_jobs
                    matched_jobs = match_jobs(parsed["text"], job_data["jobs"][:30], top_k=15)
            except Exception:
                pass

        # Generate interview questions
        try:
            interview_questions = generate_interview_questions(
                skills_data, parsed.get("sections", {}), count=15
            )
        except Exception:
            interview_questions = {"behavioral": [], "technical": [], "situational": [], "role_based": [], "total": 0}

        # Generate resume rewrite suggestions
        try:
            rewrite_result = rewrite_resume(parsed.get("sections", {}), skills_data, target_kw_list)
        except Exception:
            rewrite_result = {"rewritten_sections": {}, "improvements_count": 0, "score_boost_estimate": 0, "tips": []}

    elapsed = round(time.time() - start_time, 2)

    # Log analysis
    try:
        log_analysis(user["id"], file.filename or "unknown.pdf", ats_score.get("total_score", 0), len(skills_data.get("skills", [])))
    except Exception:
        pass

    cleanup()

    return {
        "success": True,
        "elapsed_seconds": elapsed,
        "resume": {
            "page_count": parsed["page_count"],
            "word_count": parsed["quality_signals"]["word_count"],
            "contact_info": parsed["contact_info"],
            "sections_found": list(parsed["sections"].keys()),
        },
        "ats_score": ats_score,
        "skills": skills_data,
        "career_paths": career_paths,
        "matched_jobs": matched_jobs,
        "interview_questions": interview_questions,
        "rewrite_suggestions": rewrite_result,
    }


# ──────────────────────────────────────────────
# Jobs (auth required)
# ──────────────────────────────────────────────
@app.get("/jobs")
async def get_jobs(refresh: bool = Query(default=False), user: dict = Depends(get_current_user)):
    try:
        result = await aggregate_jobs(force_refresh=refresh)
        return result
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch jobs: {str(e)}")


# ──────────────────────────────────────────────
# Career paths helper
# ──────────────────────────────────────────────
def _get_career_recommendations(skills_data: dict) -> list[dict]:
    career_path_file = os.path.join(os.path.dirname(__file__), "data", "career_paths.json")
    if not os.path.exists(career_path_file):
        return []

    with open(career_path_file, "r", encoding="utf-8") as f:
        career_data = json.load(f)

    user_skills = {s["name"].lower() for s in skills_data.get("skills", [])}
    if not user_skills:
        return []

    recommendations = []
    for path in career_data.get("career_paths", []):
        for next_role in path.get("next_roles", []):
            required = {s.lower() for s in next_role.get("required_skills", [])}
            overlap = user_skills & required
            missing = required - user_skills
            if overlap and len(overlap) >= 1:
                match_pct = round(len(overlap) / len(required) * 100) if required else 0
                recommendations.append({
                    "title": next_role["title"],
                    "from_role": path["current_role"],
                    "match_percentage": match_pct,
                    "skills_have": sorted(overlap),
                    "skills_missing": sorted(missing),
                    "timeline": next_role.get("timeline", "1-3 years"),
                })

    recommendations.sort(key=lambda r: r["match_percentage"], reverse=True)
    seen_titles = set()
    unique = []
    for rec in recommendations:
        if rec["title"] not in seen_titles:
            seen_titles.add(rec["title"])
            unique.append(rec)
        if len(unique) >= 6:
            break
    return unique


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), reload=True, workers=1)
