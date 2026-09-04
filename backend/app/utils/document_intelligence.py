from __future__ import annotations

import re
from typing import Any

DOCUMENT_RULES: list[tuple[str, str, tuple[str, ...], float]] = [
    ("cv", "resume", ("curriculum vitae", "professional summary", "work experience", "employment history", "core competencies"), 0.30),
    ("certification", "professional_certification", ("certification", "certified", "credential id", "credential number", "certificate of", "certification number"), 0.34),
    ("education", "degree_certificate", ("degree certificate", "bachelor of", "master of", "master's degree", "bachelor's degree", "doctor of philosophy", "diploma certificate"), 0.34),
    ("education", "transcript", ("academic transcript", "transcript of records", "semester", "grade point average", "gpa"), 0.30),
    ("education", "mark_sheet", ("mark sheet", "marksheet", "statement of marks", "marks obtained"), 0.30),
    ("employment", "offer_letter", ("offer letter", "letter of offer", "employment offer", "appointment letter"), 0.36),
    ("employment", "experience_letter", ("experience letter", "employment certificate", "certificate of employment", "worked with"), 0.34),
    ("employment", "relieving_letter", ("relieving letter", "relieved from services", "release letter"), 0.36),
    ("employment", "appraisal", ("performance appraisal", "appraisal letter", "performance review"), 0.34),
    ("employment", "salary_evidence", ("salary slip", "payslip", "pay slip", "gross salary", "net salary"), 0.34),
    ("achievement", "award", ("award", "recognition", "employee of the year", "certificate of appreciation"), 0.30),
    ("project", "project_evidence", ("project completion", "project summary", "statement of work", "project deliverable"), 0.30),
    ("reference", "recommendation", ("letter of recommendation", "recommendation letter", "professional reference"), 0.34),
    ("publication", "publication", ("journal", "conference paper", "publication", "doi:"), 0.28),
]


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip().lower()


def classify_document(filename: str, text: str) -> dict[str, Any]:
    """Classify by content. Filename is only a weak tie-breaker and never sufficient by itself."""
    body = _clean_text(text)
    filename_hint = _clean_text(filename)
    if not body or body in {"scanned page with no readable text", "no readable text", "unreadable scan"}:
        return {
            "category": "other",
            "subcategory": "unknown",
            "confidence": 0.0,
            "reason": "No readable document content was available; document requires review or OCR.",
        }

    scores: dict[tuple[str, str], float] = {}
    hits: dict[tuple[str, str], list[str]] = {}
    for category, subtype, terms, weight in DOCUMENT_RULES:
        matched = [term for term in terms if term in body]
        if matched:
            key = (category, subtype)
            scores[key] = scores.get(key, 0.0) + min(len(matched), 4) * weight
            hits.setdefault(key, []).extend(matched[:4])

    cv_sections = sum(term in body for term in ("experience", "education", "skills", "certifications", "projects", "professional summary"))
    if cv_sections >= 3:
        scores[("cv", "resume")] = max(scores.get(("cv", "resume"), 0.0), 0.92)
        hits.setdefault(("cv", "resume"), []).append(f"{cv_sections} career sections detected")

    strong = [key for key, score in scores.items() if score >= 0.68]
    if strong:
        best = max(strong, key=lambda k: scores[k])
    elif scores:
        best = max(scores, key=lambda k: scores[k])
    else:
        return {
            "category": "other",
            "subcategory": "needs_review",
            "confidence": 0.25,
            "reason": "The content did not contain enough document-specific signals for a safe classification.",
        }

    raw = scores[best]
    confidence = round(min(0.98, 0.45 + raw * 0.42), 2)
    reason = "Detected from document content: " + ", ".join(dict.fromkeys(hits.get(best, [])))
    if filename_hint and any(token in filename_hint for token in ("cv", "resume", "certificate", "degree", "transcript")):
        reason += ". Filename was treated only as a supporting hint."
    return {"category": best[0], "subcategory": best[1], "confidence": confidence, "reason": reason}

SECTION_ALIASES: dict[str, set[str]] = {
    "summary": {"summary", "professional summary", "profile", "professional profile", "about me", "career summary"},
    "experience": {"experience", "professional experience", "work experience", "employment", "employment history", "work history"},
    "education": {"education", "academic background", "academic qualifications", "qualifications"},
    "certifications": {"certifications", "certificates", "certifications & credentials", "credentials", "professional certifications", "training & certifications"},
    "skills": {"skills", "technical skills", "it skills", "core skills", "technologies", "technical expertise", "competencies", "core competencies"},
    "projects": {"projects", "key projects", "selected projects", "project experience"},
    "achievements": {"achievements", "key achievements", "accomplishments", "awards", "honors"},
    "publications": {"publications", "papers", "research"},
    "languages": {"languages", "language skills"},
    "memberships": {"memberships", "professional memberships", "affiliations"},
    "training": {"training", "courses", "professional training"},
}


def normalize_section_heading(line: str) -> str | None:
    candidate = re.sub(r"[^a-z0-9&+ ]", " ", (line or "").lower())
    candidate = re.sub(r"\s+", " ", candidate).strip()
    if len(candidate) > 60:
        return None
    for section, aliases in SECTION_ALIASES.items():
        if candidate in aliases:
            return section
    return None


def segment_sections(text: str) -> dict[str, str]:
    """Segment CV text before domain extraction to prevent cross-section contamination."""
    sections: dict[str, list[str]] = {key: [] for key in SECTION_ALIASES}
    current: str | None = None
    for raw_line in (text or "").splitlines():
        line = raw_line.strip()
        heading = normalize_section_heading(line)
        if heading:
            current = heading
            continue
        if current:
            sections[current].append(raw_line)
    return {key: "\n".join(lines).strip() for key, lines in sections.items() if any(line.strip() for line in lines)}
