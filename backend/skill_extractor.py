"""
ResuMatch AI — Skill Extractor
Extracts skills from resume text using spaCy NER + taxonomy pattern matching.
Identifies hard skills, soft skills, and years of experience.
"""

import re
import json
import os
from typing import Optional

# Lazy-loaded spaCy model singleton
_nlp = None
_taxonomy = None


def _get_nlp():
    """Lazy load spaCy model to save memory on startup."""
    global _nlp
    if _nlp is None:
        import spacy
        _nlp = spacy.load("en_core_web_sm")
    return _nlp


def _get_taxonomy() -> dict:
    """Load and cache skills taxonomy."""
    global _taxonomy
    if _taxonomy is None:
        taxonomy_path = os.path.join(os.path.dirname(__file__), "data", "skills_taxonomy.json")
        with open(taxonomy_path, "r", encoding="utf-8") as f:
            _taxonomy = json.load(f)
    return _taxonomy


def extract_skills(text: str) -> dict:
    """
    Extract skills from resume text using pattern matching and NER.
    
    Returns:
        {
            "skills": [{"name": str, "category": str, "proficiency": str, "years": int|None}],
            "total_years": int|None,
            "skill_locations": {"skill_name": ["section_name", ...]}
        }
    """
    taxonomy = _get_taxonomy()
    aliases = taxonomy["aliases"]
    categories = taxonomy["categories"]
    
    text_lower = text.lower()
    found_skills = {}
    skill_locations = {}
    
    # --- Phase 1: Direct taxonomy matching ---
    # Sort aliases by length (longest first) to avoid partial matches
    sorted_aliases = sorted(aliases.keys(), key=len, reverse=True)
    
    for alias in sorted_aliases:
        canonical = aliases[alias]
        if canonical in found_skills:
            continue
        
        # Use word boundary matching
        pattern = r"(?<![a-zA-Z])" + re.escape(alias) + r"(?![a-zA-Z])"
        if re.search(pattern, text_lower):
            category = categories.get(canonical, "other")
            found_skills[canonical] = {
                "name": canonical,
                "category": category,
                "proficiency": "unknown",
                "years": None,
            }
    
    # --- Phase 2: spaCy NER for additional entity extraction ---
    nlp = _get_nlp()
    # Process only first 100K chars to stay within memory limits
    doc = nlp(text[:100000])
    
    for ent in doc.ents:
        if ent.label_ in ("ORG", "PRODUCT"):
            ent_lower = ent.text.lower().strip()
            if ent_lower in aliases and aliases[ent_lower] not in found_skills:
                canonical = aliases[ent_lower]
                found_skills[canonical] = {
                    "name": canonical,
                    "category": categories.get(canonical, "other"),
                    "proficiency": "unknown",
                    "years": None,
                }
    
    # --- Phase 3: Extract years of experience per skill ---
    year_patterns = [
        # "5+ years of Python" or "5 years experience with React"
        r"(\d+)\+?\s*(?:years?|yrs?)[\s\w]*(?:of|with|in|using)?\s+([a-zA-Z\+\#\.\/\s]{2,30})",
        # "Python (5 years)" or "React - 3 years"
        r"([a-zA-Z\+\#\.\/]+)\s*[\(\-–:]\s*(\d+)\+?\s*(?:years?|yrs?)",
        # "experienced in X for Y years"
        r"(?:experienced|proficient|expert)\s+(?:in|with)\s+([a-zA-Z\+\#\.\/\s]{2,30})\s+(?:for\s+)?(\d+)\+?\s*(?:years?|yrs?)",
    ]
    
    for pattern in year_patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            groups = match.groups()
            if groups[0].isdigit():
                years = int(groups[0])
                skill_text = groups[1].strip().lower()
            else:
                skill_text = groups[0].strip().lower()
                years = int(groups[1]) if groups[1].isdigit() else None
            
            # Resolve alias
            if skill_text in aliases:
                canonical = aliases[skill_text]
                if canonical in found_skills and years:
                    found_skills[canonical]["years"] = max(
                        found_skills[canonical]["years"] or 0, years
                    )
    
    # --- Phase 4: Determine proficiency levels ---
    for skill_name, skill_data in found_skills.items():
        years = skill_data["years"]
        if years is not None:
            if years >= 5:
                skill_data["proficiency"] = "expert"
            elif years >= 3:
                skill_data["proficiency"] = "advanced"
            elif years >= 1:
                skill_data["proficiency"] = "intermediate"
            else:
                skill_data["proficiency"] = "beginner"
        else:
            # Estimate based on mention frequency
            count = len(re.findall(
                re.escape(skill_name.lower()), text_lower
            ))
            if count >= 5:
                skill_data["proficiency"] = "advanced"
            elif count >= 2:
                skill_data["proficiency"] = "intermediate"
            else:
                skill_data["proficiency"] = "beginner"
    
    # --- Phase 5: Total years of experience ---
    total_years = _extract_total_years(text)
    
    # --- Phase 6: Skill location tracking (for ATS keyword placement) ---
    skill_locations = _track_skill_locations(text, found_skills)
    
    return {
        "skills": list(found_skills.values()),
        "total_years": total_years,
        "skill_locations": skill_locations,
    }


def _extract_total_years(text: str) -> Optional[int]:
    """Extract total years of professional experience."""
    patterns = [
        r"(\d+)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*(?:professional|total|overall|industry)?\s*experience",
        r"(?:over|more than|approximately|about)\s*(\d+)\+?\s*(?:years?|yrs?)",
    ]
    
    max_years = None
    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            years = int(match.group(1))
            if years <= 50:  # sanity check
                max_years = max(max_years or 0, years)
    
    return max_years


def _track_skill_locations(text: str, skills: dict) -> dict:
    """
    Track where each skill appears in the resume (summary, experience, skills section, etc.)
    Used for ATS keyword placement scoring.
    """
    from parser import _extract_sections
    
    sections = _extract_sections(text)
    locations = {}
    
    for skill_name in skills:
        skill_lower = skill_name.lower()
        found_in = []
        
        for section_name, section_text in sections.items():
            if re.search(r"(?<![a-zA-Z])" + re.escape(skill_lower) + r"(?![a-zA-Z])",
                        section_text.lower()):
                found_in.append(section_name)
        
        locations[skill_name] = found_in
    
    return locations


def get_skill_demand(skill_name: str) -> int:
    """Get market demand weight for a skill (0-100)."""
    taxonomy = _get_taxonomy()
    return taxonomy.get("demand_weights", {}).get(skill_name, 40)


def unload_model():
    """Explicitly unload spaCy model to free memory."""
    global _nlp
    _nlp = None
