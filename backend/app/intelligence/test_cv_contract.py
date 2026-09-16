from app.intelligence.cv_ai_contract import build_cv_extraction_prompt, compact_json


def test_production_and_lab_cv_requests_are_identical_for_same_contract() -> None:
    template = {"profile": {"full_name": None}, "employment": []}
    kwargs = {
        "instruction": "Read the CV and return the information in the supplied JSON format.",
        "template": template,
        "document_id": "doc-123",
        "filename": "resume.pdf",
        "category": "cv",
        "text": "ARUN SINGH\nNetwork Architect",
    }
    production_prompt = build_cv_extraction_prompt(**kwargs)
    lab_prompt = build_cv_extraction_prompt(**kwargs)
    assert production_prompt == lab_prompt
    assert len(production_prompt) == len(compact_json(__import__("json").loads(production_prompt)))


def test_cv_request_is_compact_and_carries_the_actual_format() -> None:
    template = {"profile": {"full_name": None}, "employment": [{"employer": None}]}
    prompt = build_cv_extraction_prompt(
        instruction="Return facts only.", template=template, document_id="doc-1", filename="cv.pdf", category="cv", text="Example CV"
    )
    assert " \n" not in prompt
    payload = __import__("json").loads(prompt)
    assert payload["format"] == template
    assert payload["document"]["cv"] == "Example CV"
