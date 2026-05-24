"""
ResuMatch AI — PDF Resume Parser
Extracts text, detects layout issues, and segments sections from PDF resumes.
Uses PyMuPDF (fitz) for zero-dependency PDF parsing.
"""

import re
import math
import fitz  # PyMuPDF
from typing import Optional


# Standard resume section headers
SECTION_HEADERS = [
    "summary", "objective", "profile", "about",
    "experience", "work experience", "employment", "professional experience", "work history",
    "education", "academic", "qualifications",
    "skills", "technical skills", "core competencies", "technologies", "tech stack",
    "projects", "portfolio",
    "certifications", "certificates", "licenses",
    "awards", "honors", "achievements",
    "publications", "research",
    "volunteer", "volunteering",
    "interests", "hobbies",
    "references", "languages",
]

SECTION_PATTERN = re.compile(
    r"^\s*(" + "|".join(re.escape(h) for h in SECTION_HEADERS) + r")\s*[:\-–—]?\s*$",
    re.IGNORECASE | re.MULTILINE,
)

# Contact info patterns
EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
PHONE_PATTERN = re.compile(r"[\+]?[(]?[0-9]{1,4}[)]?[-\s./0-9]{7,15}")
LINKEDIN_PATTERN = re.compile(r"linkedin\.com/in/[\w\-]+", re.IGNORECASE)
URL_PATTERN = re.compile(r"https?://[^\s<>\"]+|www\.[^\s<>\"]+")


def extract_text_from_pdf(file_bytes: bytes) -> dict:
    """
    Extract text and metadata from a PDF resume.
    Returns dict with text, pages, metadata, and quality signals.
    """
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    
    full_text = ""
    page_texts = []
    total_images = 0
    total_tables = 0
    has_multi_column = False
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")
        page_texts.append(text)
        full_text += text + "\n"
        
        # Count images
        total_images += len(page.get_images(full=True))
        
        # Detect multi-column layout
        if _detect_multi_column(page):
            has_multi_column = True
        
        # Simple table detection via line drawings
        drawings = page.get_drawings()
        horizontal_lines = sum(1 for d in drawings for item in d.get("items", [])
                              if item[0] == "l" and abs(item[1].y - item[2].y) < 2)
        if horizontal_lines > 3:
            total_tables += 1
    
    doc.close()
    
    # Extract contact info
    contact_info = _extract_contact_info(full_text)
    
    # Detect scrambled text
    scramble_score = _detect_scrambled_text(full_text)
    
    # Extract sections
    sections = _extract_sections(full_text)
    
    return {
        "text": full_text.strip(),
        "page_count": len(page_texts),
        "page_texts": page_texts,
        "contact_info": contact_info,
        "sections": sections,
        "quality_signals": {
            "scramble_score": scramble_score,
            "has_multi_column": has_multi_column,
            "image_count": total_images,
            "table_count": total_tables,
            "char_count": len(full_text),
            "word_count": len(full_text.split()),
        },
    }


def _detect_multi_column(page) -> bool:
    """
    Detect multi-column layout by analyzing text block x-positions.
    If blocks cluster into 2+ distinct x-position groups, it's multi-column.
    """
    blocks = page.get_text("dict")["blocks"]
    text_blocks = [b for b in blocks if b.get("type") == 0]  # text blocks only
    
    if len(text_blocks) < 4:
        return False
    
    # Get x-positions of block origins
    x_positions = sorted(set(round(b["bbox"][0] / 50) * 50 for b in text_blocks))
    
    # If blocks start at 3+ significantly different x positions, likely multi-column
    if len(x_positions) >= 3:
        spread = x_positions[-1] - x_positions[0]
        if spread > 150:  # significant horizontal spread
            return True
    
    return False


def _detect_scrambled_text(text: str) -> float:
    """
    Detect scrambled/garbled text using entropy and character ratio analysis.
    Returns a score 0-1 where 1 = perfectly clean, 0 = completely scrambled.
    """
    if not text or len(text) < 50:
        return 0.0
    
    # Check ratio of readable characters
    readable = sum(1 for c in text if c.isalnum() or c.isspace() or c in ".,;:!?'-/@#$%&*()")
    ratio = readable / len(text)
    
    # Check for unusual character sequences (e.g., fi ligature issues)
    words = text.split()
    if not words:
        return 0.0
    
    # Average word length — scrambled text often has very long "words"
    avg_word_len = sum(len(w) for w in words) / len(words)
    word_score = 1.0 if avg_word_len < 12 else max(0.0, 1.0 - (avg_word_len - 12) / 20)
    
    # Shannon entropy — natural text has entropy ~4.0-4.5 for English
    entropy = _shannon_entropy(text)
    entropy_score = 1.0 if 3.5 <= entropy <= 5.0 else max(0.0, 1.0 - abs(entropy - 4.25) / 4.0)
    
    return round(min(ratio, word_score, entropy_score), 3)


def _shannon_entropy(text: str) -> float:
    """Calculate Shannon entropy of text."""
    if not text:
        return 0.0
    freq = {}
    for char in text.lower():
        freq[char] = freq.get(char, 0) + 1
    length = len(text)
    return -sum((count / length) * math.log2(count / length) for count in freq.values())


def _extract_contact_info(text: str) -> dict:
    """Extract email, phone, LinkedIn, and other URLs from text."""
    emails = EMAIL_PATTERN.findall(text)
    phones = PHONE_PATTERN.findall(text)
    linkedin = LINKEDIN_PATTERN.findall(text)
    urls = URL_PATTERN.findall(text)
    
    # Filter out LinkedIn from generic URLs
    other_urls = [u for u in urls if "linkedin.com" not in u.lower()]
    
    return {
        "email": emails[0] if emails else None,
        "phone": phones[0].strip() if phones else None,
        "linkedin": linkedin[0] if linkedin else None,
        "website": other_urls[0] if other_urls else None,
        "has_email": bool(emails),
        "has_phone": bool(phones),
        "has_linkedin": bool(linkedin),
    }


def _extract_sections(text: str) -> dict:
    """
    Split resume text into named sections based on standard headers.
    Returns dict mapping section names to their content.
    """
    sections = {}
    lines = text.split("\n")
    current_section = "header"
    current_content = []
    
    for line in lines:
        stripped = line.strip().lower()
        # Remove common decorators
        clean = re.sub(r"[:\-–—_|]", "", stripped).strip()
        
        matched_header = None
        for header in SECTION_HEADERS:
            if clean == header or stripped == header:
                matched_header = header
                break
        
        if matched_header:
            # Save previous section
            if current_content:
                sections[current_section] = "\n".join(current_content).strip()
            current_section = _normalize_section_name(matched_header)
            current_content = []
        else:
            current_content.append(line)
    
    # Save last section
    if current_content:
        sections[current_section] = "\n".join(current_content).strip()
    
    return sections


def _normalize_section_name(header: str) -> str:
    """Normalize section header to canonical name."""
    mapping = {
        "summary": "summary", "objective": "summary", "profile": "summary", "about": "summary",
        "experience": "experience", "work experience": "experience",
        "employment": "experience", "professional experience": "experience", "work history": "experience",
        "education": "education", "academic": "education", "qualifications": "education",
        "skills": "skills", "technical skills": "skills",
        "core competencies": "skills", "technologies": "skills", "tech stack": "skills",
        "projects": "projects", "portfolio": "projects",
        "certifications": "certifications", "certificates": "certifications", "licenses": "certifications",
        "awards": "awards", "honors": "awards", "achievements": "awards",
        "publications": "publications", "research": "publications",
        "volunteer": "volunteer", "volunteering": "volunteer",
        "interests": "interests", "hobbies": "interests",
        "references": "references", "languages": "languages",
    }
    return mapping.get(header.lower(), header.lower())
