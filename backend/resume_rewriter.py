"""
ResuMatch AI — Resume Rewriter (ATS-Friendly)
Rule-based engine that transforms resume bullet points for ATS optimization.
No LLM needed — uses pattern matching, action verb replacement, and keyword injection.
"""

import re
import random
from typing import Optional


# ──────────────────────────────────────────────
# Action verb dictionaries
# ──────────────────────────────────────────────

WEAK_VERBS = {
    "did": ["Executed", "Accomplished", "Delivered"],
    "made": ["Developed", "Created", "Produced"],
    "worked on": ["Engineered", "Spearheaded", "Drove"],
    "worked with": ["Collaborated with", "Partnered with", "Coordinated with"],
    "helped": ["Facilitated", "Enabled", "Supported"],
    "was responsible for": ["Managed", "Oversaw", "Directed"],
    "responsible for": ["Led", "Managed", "Orchestrated"],
    "used": ["Leveraged", "Utilized", "Implemented"],
    "got": ["Achieved", "Secured", "Attained"],
    "ran": ["Managed", "Directed", "Operated"],
    "put together": ["Assembled", "Compiled", "Consolidated"],
    "set up": ["Established", "Configured", "Deployed"],
    "came up with": ["Devised", "Conceptualized", "Pioneered"],
    "looked at": ["Analyzed", "Evaluated", "Assessed"],
    "checked": ["Audited", "Validated", "Verified"],
    "fixed": ["Resolved", "Remediated", "Debugged"],
    "changed": ["Transformed", "Revamped", "Optimized"],
    "improved": ["Enhanced", "Optimized", "Elevated"],
    "built": ["Architected", "Engineered", "Constructed"],
    "wrote": ["Authored", "Composed", "Documented"],
    "led": ["Spearheaded", "Championed", "Directed"],
    "managed": ["Orchestrated", "Oversaw", "Administered"],
    "created": ["Designed", "Developed", "Pioneered"],
    "started": ["Launched", "Initiated", "Founded"],
    "increased": ["Boosted", "Amplified", "Accelerated"],
    "decreased": ["Reduced", "Minimized", "Streamlined"],
    "handled": ["Managed", "Administered", "Coordinated"],
    "talked to": ["Consulted with", "Engaged", "Briefed"],
    "told": ["Communicated", "Conveyed", "Presented"],
    "learned": ["Mastered", "Acquired proficiency in", "Developed expertise in"],
    "tried": ["Implemented", "Piloted", "Experimented with"],
}

POWER_VERBS_BY_CATEGORY = {
    "leadership": ["Spearheaded", "Championed", "Directed", "Orchestrated", "Mobilized"],
    "technical": ["Engineered", "Architected", "Implemented", "Optimized", "Automated"],
    "analytical": ["Analyzed", "Evaluated", "Assessed", "Diagnosed", "Investigated"],
    "creative": ["Designed", "Innovated", "Pioneered", "Conceptualized", "Crafted"],
    "communication": ["Articulated", "Presented", "Advocated", "Negotiated", "Facilitated"],
    "achievement": ["Delivered", "Achieved", "Exceeded", "Surpassed", "Accomplished"],
}

# Filler words and phrases to remove
FILLER_PATTERNS = [
    (r"\bI\b ", ""),
    (r"\bmy\b ", ""),
    (r"\bMe\b ", ""),
    (r"^[-\u2022\u25cf\u25cb\u2023\u2043]\s*", ""),  # bullet chars
    (r"\s+", " "),
]

# Quantification suggestions
QUANTIFY_HINTS = {
    "team": "Specify team size (e.g., 'a team of 8 engineers')",
    "project": "Add project impact (e.g., 'serving 10K+ users')",
    "improve": "Add percentage (e.g., 'improved by 35%')",
    "increase": "Add metric (e.g., 'increased revenue by $200K')",
    "reduce": "Add numbers (e.g., 'reduced load time by 60%')",
    "manage": "Add scope (e.g., 'managed $1.2M budget')",
    "develop": "Add scale (e.g., 'developed 15 microservices')",
    "support": "Add user count (e.g., 'supporting 5,000+ daily users')",
    "deploy": "Add frequency (e.g., 'deployed 50+ releases per quarter')",
    "train": "Add count (e.g., 'trained 20+ junior developers')",
}


def rewrite_resume(
    sections: dict,
    skills_data: dict,
    target_keywords: Optional[list[str]] = None,
) -> dict:
    """
    Rewrite resume sections for ATS optimization.

    Returns:
        {
            "rewritten_sections": {
                "experience": [{"original": str, "rewritten": str, "changes": [str]}],
                ...
            },
            "improvements_count": int,
            "score_boost_estimate": int,
            "keyword_insertions": [{"keyword": str, "inserted_in": str}],
            "summary": str
        }
    """
    user_skills = {s["name"] for s in skills_data.get("skills", [])}
    rewritten = {}
    total_improvements = 0
    keyword_insertions = []

    # Process each section
    for section_name, section_text in sections.items():
        if section_name in ("header", "references", "interests"):
            continue

        bullets = _split_into_bullets(section_text)
        rewritten_bullets = []

        for bullet in bullets:
            if len(bullet.strip()) < 10:
                continue

            result = _rewrite_bullet(bullet, user_skills, target_keywords)
            rewritten_bullets.append(result)
            total_improvements += len(result["changes"])

            if result.get("keywords_added"):
                for kw in result["keywords_added"]:
                    keyword_insertions.append({"keyword": kw, "inserted_in": section_name})

        if rewritten_bullets:
            rewritten[section_name] = rewritten_bullets

    # Generate summary section if missing
    summary_suggestion = None
    if "summary" not in sections or len(sections.get("summary", "").strip()) < 20:
        summary_suggestion = _generate_summary(skills_data, target_keywords)

    score_boost = min(25, total_improvements * 3)

    return {
        "rewritten_sections": rewritten,
        "improvements_count": total_improvements,
        "score_boost_estimate": score_boost,
        "keyword_insertions": keyword_insertions,
        "summary_suggestion": summary_suggestion,
        "tips": _generate_tips(sections, skills_data),
    }


def _split_into_bullets(text: str) -> list[str]:
    """Split section text into individual bullet points."""
    lines = text.split("\n")
    bullets = []
    current = ""

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if current:
                bullets.append(current.strip())
                current = ""
            continue

        # Detect bullet start
        if re.match(r"^[-\u2022\u25cf\u2023\u2043*>]|\d+[.)]\s", stripped):
            if current:
                bullets.append(current.strip())
            current = stripped
        elif current:
            current += " " + stripped
        else:
            current = stripped

    if current:
        bullets.append(current.strip())

    return bullets


def _rewrite_bullet(
    bullet: str,
    user_skills: set,
    target_keywords: Optional[list[str]] = None,
) -> dict:
    """Rewrite a single bullet point for ATS optimization."""
    original = bullet
    rewritten = bullet
    changes = []
    keywords_added = []

    # 1. Remove filler words and pronouns
    for pattern, replacement in FILLER_PATTERNS:
        new_text = re.sub(pattern, replacement, rewritten, flags=re.IGNORECASE)
        if new_text != rewritten:
            rewritten = new_text

    rewritten = rewritten.strip()

    # 2. Replace weak verbs with power verbs
    for weak, strong_options in WEAK_VERBS.items():
        pattern = r"(?i)^" + re.escape(weak) + r"\b"
        if re.search(pattern, rewritten):
            replacement = random.choice(strong_options)
            rewritten = re.sub(pattern, replacement, rewritten, count=1)
            changes.append(f"Replaced '{weak}' with '{replacement}'")
            break

    # Also check mid-sentence weak verbs
    for weak, strong_options in WEAK_VERBS.items():
        pattern = r"(?i)\b" + re.escape(weak) + r"\b"
        if re.search(pattern, rewritten) and weak not in rewritten[:len(weak)+2].lower():
            replacement = strong_options[0].lower()
            rewritten = re.sub(pattern, replacement, rewritten, count=1)
            changes.append(f"Strengthened verb '{weak}'")
            break

    # 3. Ensure starts with action verb (capitalize first word)
    if rewritten and rewritten[0].islower():
        rewritten = rewritten[0].upper() + rewritten[1:]

    # 4. Check for quantification opportunity
    has_numbers = bool(re.search(r"\d+", rewritten))
    if not has_numbers:
        for keyword, hint in QUANTIFY_HINTS.items():
            if keyword.lower() in rewritten.lower():
                changes.append(f"Add metrics: {hint}")
                break

    # 5. Add missing target keywords naturally
    if target_keywords:
        bullet_lower = rewritten.lower()
        for kw in target_keywords:
            if kw.lower() not in bullet_lower and kw.lower() not in " ".join(user_skills).lower():
                # Only add if contextually relevant
                if _is_keyword_relevant(rewritten, kw):
                    rewritten = _inject_keyword(rewritten, kw)
                    keywords_added.append(kw)
                    changes.append(f"Integrated keyword '{kw}'")
                    break  # Max 1 keyword per bullet

    # 6. Remove trailing periods inconsistency
    if rewritten and rewritten[-1] not in ".!":
        rewritten += "."

    # 7. Ensure proper length (not too short)
    if len(rewritten) < 30 and not changes:
        changes.append("Consider expanding with more detail and metrics")

    return {
        "original": original,
        "rewritten": rewritten if rewritten != original else original,
        "changes": changes,
        "keywords_added": keywords_added,
        "improved": rewritten != original,
    }


def _is_keyword_relevant(text: str, keyword: str) -> bool:
    """Check if a keyword is contextually relevant to a bullet."""
    tech_contexts = {
        "React": ["frontend", "ui", "component", "interface", "web", "app"],
        "Python": ["backend", "script", "data", "automat", "api", "server"],
        "AWS": ["cloud", "deploy", "infra", "server", "scale", "host"],
        "Docker": ["deploy", "container", "infra", "devops", "ci"],
        "TypeScript": ["javascript", "frontend", "web", "type", "app"],
    }
    contexts = tech_contexts.get(keyword, [])
    if not contexts:
        return False
    text_lower = text.lower()
    return any(ctx in text_lower for ctx in contexts)


def _inject_keyword(text: str, keyword: str) -> str:
    """Naturally inject a keyword into a bullet point."""
    # Add at end as a tool/technology mention
    if text.endswith("."):
        text = text[:-1]
    return f"{text} utilizing {keyword}."


def _generate_summary(skills_data: dict, target_keywords: Optional[list[str]] = None) -> str:
    """Generate a professional summary suggestion."""
    skills = skills_data.get("skills", [])
    years = skills_data.get("total_years")
    top_skills = sorted(skills, key=lambda s: s.get("demand", 0), reverse=True)[:5]
    skill_names = [s["name"] for s in top_skills]

    years_text = f"with {years}+ years of experience " if years else ""
    skills_text = ", ".join(skill_names[:3]) if skill_names else "modern technologies"
    extra = f" and {skill_names[3]}" if len(skill_names) > 3 else ""

    return (
        f"Results-driven software professional {years_text}"
        f"specializing in {skills_text}{extra}. "
        f"Proven track record of delivering scalable, high-quality solutions "
        f"that drive business impact. Passionate about clean code, "
        f"continuous improvement, and cross-functional collaboration."
    )


def _generate_tips(sections: dict, skills_data: dict) -> list[str]:
    """Generate actionable resume improvement tips."""
    tips = []

    if "summary" not in sections:
        tips.append("Add a Professional Summary at the top -- it's the first thing recruiters read")

    experience_text = sections.get("experience", "")
    if experience_text:
        bullets = _split_into_bullets(experience_text)
        num_without_numbers = sum(1 for b in bullets if not re.search(r"\d+", b))
        if num_without_numbers > len(bullets) * 0.5:
            tips.append(f"{num_without_numbers} of {len(bullets)} bullet points lack metrics -- add numbers to strengthen impact")

    skills = skills_data.get("skills", [])
    if len(skills) < 8:
        tips.append("Your skills section seems thin -- aim for 10-15 relevant technologies")

    if "projects" not in sections:
        tips.append("Consider adding a Projects section to showcase hands-on work")

    if "certifications" not in sections:
        tips.append("Adding certifications can boost ATS scores by 5-10 points")

    tips.append("Use consistent formatting: same tense, same bullet style throughout")
    tips.append("Keep resume to 1-2 pages max for best ATS compatibility")

    return tips[:6]
