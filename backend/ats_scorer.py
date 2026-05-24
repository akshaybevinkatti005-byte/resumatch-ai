"""
ResuMatch AI — ATS Ghost Score Engine
Rule-based scoring algorithm that estimates how well a resume will perform
in Applicant Tracking Systems (ATS).
"""

import re
from typing import Optional


def calculate_ghost_score(
    parsed_resume: dict,
    extracted_skills: dict,
    target_keywords: Optional[list[str]] = None,
) -> dict:
    """
    Calculate the ATS Ghost Score for a parsed resume.
    
    Weights:
        - Parsing Accuracy: 35%
        - Keyword Coverage: 30%
        - Formatting Compliance: 20%
        - Structure: 15%
    
    Args:
        parsed_resume: Output from parser.extract_text_from_pdf()
        extracted_skills: Output from skill_extractor.extract_skills()
        target_keywords: Optional list of target job keywords to check coverage against
    
    Returns:
        {
            "total_score": 0-100,
            "grade": "A" | "B" | "C" | "D" | "F",
            "breakdown": {
                "parsing": {"score": 0-100, "weight": 35, "weighted": float, "details": [str]},
                "keywords": {"score": 0-100, "weight": 30, "weighted": float, "details": [str]},
                "formatting": {"score": 0-100, "weight": 20, "weighted": float, "details": [str]},
                "structure": {"score": 0-100, "weight": 15, "weighted": float, "details": [str]},
            },
            "recommendations": [str]
        }
    """
    parsing = _score_parsing_accuracy(parsed_resume)
    keywords = _score_keyword_coverage(parsed_resume, extracted_skills, target_keywords)
    formatting = _score_formatting_compliance(parsed_resume)
    structure = _score_structure(parsed_resume)
    
    # Calculate weighted total
    total = (
        parsing["score"] * 0.35 +
        keywords["score"] * 0.30 +
        formatting["score"] * 0.20 +
        structure["score"] * 0.15
    )
    total = round(total, 1)
    
    # Grade assignment
    if total >= 90:
        grade = "A"
    elif total >= 75:
        grade = "B"
    elif total >= 60:
        grade = "C"
    elif total >= 40:
        grade = "D"
    else:
        grade = "F"
    
    # Compile recommendations
    recommendations = []
    recommendations.extend(parsing.get("recommendations", []))
    recommendations.extend(keywords.get("recommendations", []))
    recommendations.extend(formatting.get("recommendations", []))
    recommendations.extend(structure.get("recommendations", []))
    
    # Sort by priority (most impactful first)
    recommendations = recommendations[:8]  # Cap at 8 recommendations
    
    return {
        "total_score": total,
        "grade": grade,
        "breakdown": {
            "parsing": {
                "score": parsing["score"],
                "weight": 35,
                "weighted": round(parsing["score"] * 0.35, 1),
                "details": parsing["details"],
            },
            "keywords": {
                "score": keywords["score"],
                "weight": 30,
                "weighted": round(keywords["score"] * 0.30, 1),
                "details": keywords["details"],
            },
            "formatting": {
                "score": formatting["score"],
                "weight": 20,
                "weighted": round(formatting["score"] * 0.20, 1),
                "details": formatting["details"],
            },
            "structure": {
                "score": structure["score"],
                "weight": 15,
                "weighted": round(structure["score"] * 0.15, 1),
                "details": structure["details"],
            },
        },
        "recommendations": recommendations,
    }


def _score_parsing_accuracy(parsed: dict) -> dict:
    """
    Score: How cleanly can ATS systems parse this resume?
    Checks: text scrambling, multi-column layout, character encoding issues.
    """
    score = 100.0
    details = []
    recommendations = []
    signals = parsed.get("quality_signals", {})
    
    # Scramble detection (0-1 where 1 is clean)
    scramble_score = signals.get("scramble_score", 1.0)
    if scramble_score < 0.7:
        penalty = (1.0 - scramble_score) * 50
        score -= penalty
        details.append(f"Text appears scrambled (clarity: {scramble_score:.0%})")
        recommendations.append("Re-export your PDF from the source document — the text layer appears corrupted")
    elif scramble_score < 0.9:
        penalty = (1.0 - scramble_score) * 25
        score -= penalty
        details.append(f"Minor text encoding issues detected (clarity: {scramble_score:.0%})")
    else:
        details.append("Text parses cleanly ✓")
    
    # Multi-column penalty
    if signals.get("has_multi_column", False):
        score -= 25
        details.append("Multi-column layout detected — ATS may scramble reading order")
        recommendations.append("Switch to a single-column resume layout for better ATS parsing")
    else:
        details.append("Single-column layout ✓")
    
    # Word count sanity
    word_count = signals.get("word_count", 0)
    if word_count < 100:
        score -= 20
        details.append(f"Very short resume ({word_count} words)")
        recommendations.append("Your resume appears too short — aim for 400-700 words")
    elif word_count > 1500:
        score -= 10
        details.append(f"Resume may be too long ({word_count} words)")
        recommendations.append("Consider condensing your resume to 1-2 pages (400-700 words)")
    else:
        details.append(f"Good length ({word_count} words) ✓")
    
    # Page count
    page_count = parsed.get("page_count", 1)
    if page_count > 3:
        score -= 10
        details.append(f"Too many pages ({page_count})")
        recommendations.append("Keep your resume to 1-2 pages maximum")
    
    return {
        "score": max(0, min(100, round(score))),
        "details": details,
        "recommendations": recommendations,
    }


def _score_keyword_coverage(
    parsed: dict,
    skills: dict,
    target_keywords: Optional[list[str]] = None,
) -> dict:
    """
    Score: How well are keywords placed throughout the resume?
    Uses placement multiplier:
        1.0x — skill in summary + experience
        0.7x — skill only in skills section
        0.4x — skill only in roles older than 5 years
    """
    score = 0.0
    details = []
    recommendations = []
    
    skill_list = skills.get("skills", [])
    skill_locations = skills.get("skill_locations", {})
    sections = parsed.get("sections", {})
    
    if not skill_list:
        details.append("No skills detected in resume")
        recommendations.append("Add a dedicated Skills section with your technical competencies")
        return {"score": 20, "details": details, "recommendations": recommendations}
    
    # If target keywords provided, check coverage
    if target_keywords:
        found_keywords = set()
        skill_names_lower = {s["name"].lower() for s in skill_list}
        
        for keyword in target_keywords:
            if keyword.lower() in skill_names_lower:
                found_keywords.add(keyword)
        
        coverage = len(found_keywords) / len(target_keywords) if target_keywords else 0
        score = coverage * 100
        details.append(f"Job keyword coverage: {len(found_keywords)}/{len(target_keywords)} ({coverage:.0%})")
        
        missing = [k for k in target_keywords if k.lower() not in skill_names_lower]
        if missing:
            recommendations.append(f"Add these missing keywords: {', '.join(missing[:5])}")
    else:
        # Score based on placement quality
        total_placement_score = 0
        skill_count = len(skill_list)
        
        for skill in skill_list:
            locations = skill_locations.get(skill["name"], [])
            
            if "summary" in locations and "experience" in locations:
                multiplier = 1.0  # Best placement
            elif "experience" in locations:
                multiplier = 0.85
            elif "summary" in locations:
                multiplier = 0.75
            elif "skills" in locations:
                multiplier = 0.7  # Only in skills list
            elif "projects" in locations:
                multiplier = 0.6
            else:
                multiplier = 0.4  # Buried or in old sections
            
            total_placement_score += multiplier
        
        avg_placement = total_placement_score / skill_count if skill_count else 0
        score = avg_placement * 100
        
        # Bonus for skill count
        if skill_count >= 10:
            details.append(f"Good skill diversity ({skill_count} skills detected) ✓")
        elif skill_count >= 5:
            details.append(f"Moderate skill count ({skill_count} skills)")
        else:
            details.append(f"Low skill count ({skill_count} skills)")
            recommendations.append("Include more relevant skills — aim for 10-15 key technologies")
    
    # Check if skills appear in multiple sections (ideal)
    multi_section_skills = sum(
        1 for locs in skill_locations.values()
        if len(locs) >= 2
    )
    if multi_section_skills > 0:
        details.append(f"{multi_section_skills} skills appear in multiple sections ✓")
    else:
        recommendations.append("Mention your top skills in both Summary and Experience sections")
    
    # Check for skills-only listing (no context)
    if "skills" in sections and "experience" in sections:
        skills_text = sections.get("skills", "")
        if len(skills_text.split()) < 5:
            recommendations.append("Expand your Skills section with proficiency levels or categories")
    
    return {
        "score": max(0, min(100, round(score))),
        "details": details,
        "recommendations": recommendations,
    }


def _score_formatting_compliance(parsed: dict) -> dict:
    """
    Score: Does the resume use ATS-friendly formatting?
    Checks: images, tables, non-standard headings, special characters.
    """
    score = 100.0
    details = []
    recommendations = []
    signals = parsed.get("quality_signals", {})
    
    # Images penalty
    image_count = signals.get("image_count", 0)
    if image_count > 0:
        penalty = min(30, image_count * 10)
        score -= penalty
        details.append(f"{image_count} image(s) detected — ATS cannot read images")
        recommendations.append("Remove images, logos, and icons — ATS parsers cannot read visual content")
    else:
        details.append("No images (ATS-friendly) ✓")
    
    # Tables penalty
    table_count = signals.get("table_count", 0)
    if table_count > 0:
        penalty = min(20, table_count * 10)
        score -= penalty
        details.append(f"{table_count} table(s) detected — tables often break ATS parsing")
        recommendations.append("Replace tables with simple bullet-point lists")
    else:
        details.append("No tables (ATS-friendly) ✓")
    
    # Check for standard vs. non-standard section headings
    text = parsed.get("text", "")
    sections = parsed.get("sections", {})
    
    # Check for special characters in headings (emojis, symbols)
    special_char_pattern = re.compile(r"[★☆►▸●○◆◇→←↑↓✓✗✔✘⚡🔥💡🎯📧📱🏠💼🎓]")
    if special_char_pattern.search(text):
        score -= 10
        details.append("Special characters/emojis detected in text")
        recommendations.append("Remove emojis and special symbols — many ATS systems cannot parse them")
    
    # Check for headers vs fancy formatting
    lines = text.split("\n")
    all_caps_headers = sum(1 for line in lines if line.strip().isupper() and 2 < len(line.strip()) < 30)
    if all_caps_headers >= 3:
        details.append("Standard ALL CAPS headers detected ✓")
    
    return {
        "score": max(0, min(100, round(score))),
        "details": details,
        "recommendations": recommendations,
    }


def _score_structure(parsed: dict) -> dict:
    """
    Score: Does the resume have the expected structural elements?
    Checks: contact info, LinkedIn, standard sections.
    """
    score = 0.0
    details = []
    recommendations = []
    contact = parsed.get("contact_info", {})
    sections = parsed.get("sections", {})
    
    # Contact info (30 points)
    contact_score = 0
    if contact.get("has_email"):
        contact_score += 12
        details.append("Email found ✓")
    else:
        recommendations.append("Add your email address to the header")
    
    if contact.get("has_phone"):
        contact_score += 10
        details.append("Phone found ✓")
    else:
        recommendations.append("Add your phone number to the header")
    
    if contact.get("has_linkedin"):
        contact_score += 8
        details.append("LinkedIn URL found ✓")
    else:
        recommendations.append("Add your LinkedIn profile URL — recruiters look for this")
    
    score += contact_score
    
    # Standard sections (70 points)
    required_sections = {
        "experience": 25,
        "education": 20,
        "skills": 15,
        "summary": 10,
    }
    
    for section, points in required_sections.items():
        if section in sections and len(sections[section].strip()) > 10:
            score += points
            details.append(f"'{section.title()}' section found ✓")
        else:
            score += points * 0.1  # Small credit for having the resume at all
            details.append(f"'{section.title()}' section missing")
            recommendations.append(f"Add a '{section.title()}' section to your resume")
    
    return {
        "score": max(0, min(100, round(score))),
        "details": details,
        "recommendations": recommendations,
    }
