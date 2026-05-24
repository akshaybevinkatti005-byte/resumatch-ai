"""
ResuMatch AI — Interview Question Generator
Generates personalized interview questions from the user's resume
using extracted skills, experience, and job context.
100% rule-based — no LLM API needed.
"""

import random
import re
from typing import Optional


# ──────────────────────────────────────────────
# Question templates by category
# ──────────────────────────────────────────────

BEHAVIORAL_TEMPLATES = [
    "Tell me about a time you used {skill} to solve a complex problem.",
    "Describe a situation where your {skill} expertise directly impacted a project's success.",
    "Give an example of a challenge you faced while working with {skill} and how you overcame it.",
    "Walk me through a project where you had to learn {skill} quickly under pressure.",
    "Tell me about a time you had to debug a critical issue involving {skill}.",
    "Describe how you mentored or helped a teammate with {skill}.",
    "Give an example of how you improved a process or system using {skill}.",
    "Tell me about a time {skill} didn't work as expected and what you did about it.",
]

TECHNICAL_TEMPLATES = {
    "frontend": [
        "How would you optimize the rendering performance of a large {skill} application?",
        "Explain the component lifecycle in {skill} and how it affects state management.",
        "How do you handle state management in a complex {skill} application?",
        "Describe your approach to testing {skill} components — unit, integration, and E2E.",
        "How would you implement lazy loading and code splitting in {skill}?",
        "Explain how you would handle accessibility (a11y) in a {skill} application.",
        "What's your strategy for managing CSS architecture in a {skill} project?",
    ],
    "backend": [
        "How would you design a scalable REST API using {skill}?",
        "Explain how you handle authentication and authorization in {skill}.",
        "How do you approach database query optimization in a {skill} application?",
        "Describe your strategy for error handling and logging in {skill}.",
        "How would you implement rate limiting and caching in {skill}?",
        "Walk me through how you'd design a microservice using {skill}.",
        "How do you handle background jobs and async processing in {skill}?",
    ],
    "database": [
        "How would you design a schema for a multi-tenant application in {skill}?",
        "Explain your approach to database migrations and versioning with {skill}.",
        "How do you handle indexing strategies in {skill} for query performance?",
        "Describe how you'd implement data replication or sharding in {skill}.",
        "How do you approach backup, recovery, and data integrity in {skill}?",
    ],
    "devops": [
        "How would you set up a CI/CD pipeline using {skill}?",
        "Explain your approach to infrastructure-as-code with {skill}.",
        "How do you handle monitoring and alerting in a {skill} environment?",
        "Describe how you'd implement zero-downtime deployments with {skill}.",
        "How do you manage secrets and configuration in {skill}?",
    ],
    "cloud": [
        "How would you architect a highly available system on {skill}?",
        "Explain your approach to cost optimization on {skill}.",
        "How do you handle security and compliance on {skill}?",
        "Describe how you'd implement auto-scaling on {skill}.",
        "How would you design a disaster recovery strategy on {skill}?",
    ],
    "data_science": [
        "How would you approach feature engineering for a {skill} model?",
        "Explain how you evaluate model performance and handle overfitting in {skill}.",
        "How do you handle imbalanced datasets when working with {skill}?",
        "Describe your approach to model deployment and monitoring with {skill}.",
        "How would you explain a {skill} model's predictions to a non-technical stakeholder?",
    ],
    "language": [
        "What are the key differences between {skill} and its main competitors?",
        "How do you handle concurrency and parallelism in {skill}?",
        "Explain memory management best practices in {skill}.",
        "How do you approach code organization and architecture in a large {skill} codebase?",
        "What testing strategies do you use in {skill} projects?",
    ],
}

SITUATIONAL_TEMPLATES = [
    "Your team disagrees on whether to use {skill_a} or {skill_b}. How do you handle this?",
    "A production system built with {skill_a} goes down at 2 AM. Walk me through your response.",
    "You're asked to migrate a legacy system to {skill_a}. How do you plan and execute this?",
    "A junior developer is struggling with {skill_a}. How do you help them while meeting your own deadlines?",
    "Your manager asks you to deliver a {skill_a} feature in half the estimated time. What do you do?",
    "You discover a security vulnerability in your {skill_a} implementation. What's your immediate action plan?",
]

EXPERIENCE_TEMPLATES = [
    "You mentioned {years} years with {skill}. How has the ecosystem changed during that time?",
    "With your {years} years of {skill} experience, what's the most common mistake you see developers make?",
    "How has your approach to {skill} evolved over your {years} years of experience?",
]

ROLE_BASED_TEMPLATES = {
    "leadership": [
        "How do you balance hands-on coding with leadership responsibilities?",
        "Describe your approach to technical decision-making as a team lead.",
        "How do you handle underperforming team members?",
        "What's your strategy for building and scaling an engineering team?",
        "How do you prioritize technical debt vs. new feature development?",
    ],
    "senior": [
        "How do you approach system design for a new project?",
        "Describe a time you made a significant architectural decision. What was the outcome?",
        "How do you ensure code quality across a team?",
        "What's your approach to knowledge sharing and documentation?",
        "How do you handle disagreements about technical direction?",
    ],
    "general": [
        "What's your approach to continuous learning and staying current?",
        "How do you handle working with ambiguous requirements?",
        "Describe your ideal development workflow.",
        "How do you approach code reviews — both giving and receiving feedback?",
        "What project are you most proud of and why?",
    ],
}


def generate_interview_questions(
    skills_data: dict,
    resume_sections: dict,
    target_role: Optional[str] = None,
    count: int = 15,
) -> dict:
    """
    Generate personalized interview questions based on resume content.
    
    Returns:
        {
            "behavioral": [{"question": str, "skill": str, "tip": str}],
            "technical": [{"question": str, "skill": str, "category": str}],
            "situational": [{"question": str, "context": str}],
            "role_based": [{"question": str, "category": str}],
            "total": int
        }
    """
    skills = skills_data.get("skills", [])
    if not skills:
        return _empty_result()
    
    # Categorize skills by type
    skill_map = {}
    for s in skills:
        cat = s.get("category", "other")
        if cat not in skill_map:
            skill_map[cat] = []
        skill_map[cat].append(s)
    
    # Get top skills by demand/proficiency
    top_skills = sorted(skills, key=lambda s: s.get("demand", 0), reverse=True)[:10]
    expert_skills = [s for s in skills if s.get("proficiency") in ("expert", "advanced")]
    
    behavioral = _generate_behavioral(top_skills)
    technical = _generate_technical(skills, skill_map)
    situational = _generate_situational(top_skills)
    role_based = _generate_role_based(resume_sections, skills_data)
    
    # Trim to count
    per_category = max(3, count // 4)
    behavioral = behavioral[:per_category]
    technical = technical[:per_category + 2]  # More technical questions
    situational = situational[:per_category - 1]
    role_based = role_based[:per_category - 1]
    
    all_questions = behavioral + technical + situational + role_based
    
    return {
        "behavioral": behavioral,
        "technical": technical,
        "situational": situational,
        "role_based": role_based,
        "total": len(all_questions),
    }


def _generate_behavioral(skills: list) -> list:
    questions = []
    used = set()
    for skill in skills:
        template = random.choice(BEHAVIORAL_TEMPLATES)
        q = template.format(skill=skill["name"])
        if q not in used:
            used.add(q)
            questions.append({
                "question": q,
                "skill": skill["name"],
                "tip": _get_behavioral_tip(skill),
            })
    return questions


def _generate_technical(skills: list, skill_map: dict) -> list:
    questions = []
    used = set()
    for skill in skills:
        cat = skill.get("category", "other")
        templates = TECHNICAL_TEMPLATES.get(cat, TECHNICAL_TEMPLATES.get("language", []))
        if templates:
            template = random.choice(templates)
            q = template.format(skill=skill["name"])
            if q not in used:
                used.add(q)
                questions.append({
                    "question": q,
                    "skill": skill["name"],
                    "category": cat,
                })
    return questions


def _generate_situational(skills: list) -> list:
    questions = []
    if len(skills) < 2:
        return questions
    
    used = set()
    pairs = [(skills[i], skills[j]) for i in range(min(5, len(skills)))
             for j in range(i + 1, min(6, len(skills)))]
    random.shuffle(pairs)
    
    for s_a, s_b in pairs[:5]:
        template = random.choice(SITUATIONAL_TEMPLATES)
        q = template.format(skill_a=s_a["name"], skill_b=s_b["name"])
        if q not in used:
            used.add(q)
            questions.append({
                "question": q,
                "context": f"Based on your {s_a['name']} and {s_b['name']} experience",
            })
    return questions


def _generate_role_based(sections: dict, skills_data: dict) -> list:
    questions = []
    text = " ".join(sections.values()).lower() if sections else ""
    total_years = skills_data.get("total_years")
    
    # Detect seniority level
    if any(kw in text for kw in ["lead", "manager", "director", "head of", "vp "]):
        templates = ROLE_BASED_TEMPLATES["leadership"]
        category = "leadership"
    elif any(kw in text for kw in ["senior", "sr.", "principal", "staff"]) or (total_years and total_years >= 5):
        templates = ROLE_BASED_TEMPLATES["senior"]
        category = "senior"
    else:
        templates = ROLE_BASED_TEMPLATES["general"]
        category = "general"
    
    for q in templates[:4]:
        questions.append({"question": q, "category": category})
    
    # Add experience-based questions for expert skills
    expert_skills = [s for s in skills_data.get("skills", [])
                     if s.get("years") and s["years"] >= 3]
    for s in expert_skills[:2]:
        template = random.choice(EXPERIENCE_TEMPLATES)
        questions.append({
            "question": template.format(years=s["years"], skill=s["name"]),
            "category": "experience",
        })
    
    return questions


def _get_behavioral_tip(skill: dict) -> str:
    prof = skill.get("proficiency", "unknown")
    if prof in ("expert", "advanced"):
        return "Highlight leadership and complex problem-solving with this skill."
    elif prof == "intermediate":
        return "Focus on growth — show how you deepened your expertise."
    else:
        return "Emphasize eagerness to learn and any hands-on projects."


def _empty_result():
    return {
        "behavioral": [],
        "technical": [],
        "situational": [],
        "role_based": [],
        "total": 0,
    }
