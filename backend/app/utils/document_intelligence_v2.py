from __future__ import annotations

import re
from typing import Any


# Content-first document intelligence. Filename is metadata only and never contributes to a
# positive classification.
DOCUMENT_RULES: list[tuple[str, str, tuple[str, ...], float]] = [
    ("cv", "resume", ("curriculum vitae", "professional summary", "work experience", "employment history", "career history", "professional experience", "core competencies", "career profile"), 0.28),
    ("certification", "professional_certification", ("professional certification", "certification", "certified", "credential id", "credential number", "certificate of", "certification number", "issued by", "awarded by"), 0.30),
    ("education", "degree_certificate", ("degree certificate", "bachelor of", "master of", "master's degree", "bachelor's degree", "doctor of philosophy", "diploma certificate", "this is to certify that", "degree awarded"), 0.30),
    ("education", "transcript", ("academic transcript", "transcript of records", "semester", "grade point average", "gpa", "course credits"), 0.30),
    ("education", "mark_sheet", ("mark sheet", "marksheet", "statement of marks", "marks obtained", "marks secured", "marksheet cum certificate"), 0.30),
    ("employment", "offer_letter", ("offer letter", "letter of offer", "employment offer", "appointment letter", "date of joining", "joining date", "place of posting", "terms of employment", "we are pleased to offer you"), 0.32),
    ("employment", "experience_letter", ("experience letter", "employment certificate", "certificate of employment", "worked with", "period of employment", "last working day", "relieving date", "during his tenure"), 0.32),
    ("employment", "relieving_letter", ("relieving letter", "relieved from services", "release letter", "relieved from the services", "relieved of his duties"), 0.34),
    ("employment", "appraisal", ("performance appraisal", "appraisal letter", "performance review", "annual appraisal", "rating"), 0.34),
    ("employment", "salary_evidence", ("salary slip", "payslip", "pay slip", "gross salary", "net salary", "salary statement", "earnings"), 0.34),
    ("achievement", "award", ("award", "recognition", "employee of the year", "certificate of appreciation", "outstanding contribution"), 0.30),
    ("project", "project_evidence", ("project completion", "project summary", "statement of work", "project deliverable", "project completion certificate"), 0.30),
    ("reference", "recommendation", ("letter of recommendation", "recommendation letter", "professional reference"), 0.32),
    ("publication", "publication", ("journal", "conference paper", "publication", "doi:"), 0.28),
]


def _clean_text(text: str) -> str:
    text = (text or "").replace("\u200b", " ").replace("\ufeff", " ")
    return re.sub(r"\s+", " ", text).strip().lower()


def _ocr_compact(body: str) -> str:
    # OCR commonly inserts spaces inside identity identifiers. Keep a normalized compact form
    # only for identity matching; the original extracted text remains untouched for provenance.
    return re.sub(r"[^a-z0-9]", "", body.lower())


def _score(body: str, terms: tuple[str, ...], weight: float) -> tuple[float, list[str]]:
    hits = [term for term in terms if term in body]
    return min(5, len(hits)) * weight, hits[:5]


def _identity_boost(body: str) -> list[tuple[tuple[str, str], float, list[str]]]:
    results: list[tuple[tuple[str, str], float, list[str]]] = []
    upper = body.upper()
    compact = _ocr_compact(body)

    # PAN: allow OCR spacing between the five letters, four digits and final letter, and tolerate
    # common OCR spelling noise around the surrounding Indian tax authority wording.
    pan_ids = re.findall(r"\b[A-Z]{5}\s*\d{4}\s*[A-Z]\b", upper)
    pan_compact = re.findall(r"\b[a-z]{5}\d{4}[a-z]\b", compact)
    if (pan_ids or pan_compact) and any(term in compact for term in ("permanentaccountnumber", "incometaxdepartment", "incometax", "pan")):
        results.append((("identity", "pan_card"), 1.10, ["PAN-format identifier", "income-tax/PAN wording"]))

    # Aadhaar: OCR may use spaces, hyphens or X placeholders. Require both the 12-digit shape and
    # an Aadhaar/UIDAI authority signal to avoid confusing dates or phone numbers with Aadhaar.
    aadhaar = bool(re.search(r"\b\d{4}[ -]?\d{4}[ -]?\d{4}\b", upper) or re.search(r"\b\d{4}\s*\d{4}\s*[0-9X]{4}\b", upper))
    if aadhaar and any(term in compact for term in ("aadhaar", "uidai", "uniqueidentificationauthorityofindia")):
        results.append((("identity", "aadhaar_card"), 1.10, ["Aadhaar identifier pattern", "UIDAI/Aadhaar wording"]))

    if "passportnumber" in compact and ("passport" in compact or "republicofindia" in compact):
        results.append((("identity", "passport"), 1.05, ["passport number", "passport wording"]))
    return results


def classify_document(filename: str, text: str) -> dict[str, Any]:
    body = _clean_text(text)
    if not body:
        return {"category": "other", "subcategory": "unknown", "confidence": 0.0,
                "reason": "No readable text was available; document requires review."}

    scores: dict[tuple[str, str], float] = {}
    hits: dict[tuple[str, str], list[str]] = {}
    for category, subtype, terms, weight in DOCUMENT_RULES:
        score, matched = _score(body, terms, weight)
        if score:
            scores[(category, subtype)] = score
            hits[(category, subtype)] = matched

    for key, score, matched in _identity_boost(body):
        scores[key] = max(scores.get(key, 0.0), score)
        hits[key] = matched

    # A CV requires several independent section signals. This prevents one word such as
    # "certified" from classifying a resume as a certificate.
    cv_section_terms = (
        "experience", "professional experience", "employment history", "education",
        "skills", "certifications", "projects", "professional summary", "career profile",
    )
    cv_sections = sum(term in body for term in cv_section_terms)
    if cv_sections >= 3:
        key = ("cv", "resume")
        scores[key] = max(scores.get(key, 0.0), 0.95)
        hits.setdefault(key, []).append(f"{cv_sections} career sections detected")

    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    if not ranked or ranked[0][1] < 0.28:
        return {"category": "other", "subcategory": "unknown", "confidence": 0.25,
                "reason": "The extracted content did not contain enough document-specific signals for a safe classification."}

    best, raw = ranked[0]
    runner_up = ranked[1][1] if len(ranked) > 1 else 0.0
    if runner_up >= 0.70 and (raw - runner_up) < 0.12 and best[0] != "identity":
        competing = ", ".join(f"{k[0]} / {k[1]}" for k, _ in ranked[:2])
        return {"category": "other", "subcategory": "unknown", "confidence": 0.35,
                "reason": f"The content matched multiple document types too closely ({competing}); review is required."}

    confidence = round(min(0.99, 0.46 + raw * 0.44), 2)
    reason = "Detected from document content: " + ", ".join(dict.fromkeys(hits.get(best, [])))
    if filename:
        reason += ". Original filename was retained as metadata only, not used for classification."
    return {"category": best[0], "subcategory": best[1], "confidence": confidence, "reason": reason}


SECTION_ALIASES: dict[str, set[str]] = {
    "summary": {"summary", "professional summary", "profile", "professional profile", "about me", "career summary", "executive summary"},
    "experience": {"experience", "professional experience", "work experience", "employment", "employment history", "work history", "career history", "professional background", "career experience", "work experience & responsibilities"},
    "education": {"education", "academic background", "academic qualifications", "qualifications", "educational qualifications", "academic history"},
    "certifications": {"certifications", "certificates", "certifications & credentials", "credentials", "professional certifications", "training & certifications", "certification & credentials", "licenses & certifications"},
    "skills": {"skills", "technical skills", "it skills", "core skills", "technologies", "technical expertise", "competencies", "core competencies", "key skills", "areas of expertise"},
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
    if len(candidate) > 80:
        return None
    for section, aliases in SECTION_ALIASES.items():
        if candidate in aliases:
            return section
    return None


def segment_sections(text: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {key: [] for key in SECTION_ALIASES}
    current: str | None = None
    for raw_line in (text or "").replace("\r", "").splitlines():
        line = raw_line.strip()
        heading = normalize_section_heading(line)
        if heading:
            current = heading
            continue
        if current:
            sections[current].append(raw_line)
    return {key: "\n".join(lines).strip() for key, lines in sections.items() if any(line.strip() for line in lines)}
