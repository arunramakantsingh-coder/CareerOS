from app.utils.document_intelligence import classify_document, segment_sections


def test_document_sections_can_be_detected_without_career_parser():
    text = '''ARUN SINGH
PROFESSIONAL SUMMARY
Technology leader with cloud and security experience.

EXPERIENCE
Acme Corp - Technology Director
2019 - Present
Led cloud transformation and security governance.

EDUCATION
Master of Science in Computer Science
Example University
2010 - 2012

CERTIFICATIONS & CREDENTIALS
AWS Certified Solutions Architect - Associate, 2025

SKILLS
AWS, Azure, Kubernetes, Python
'''
    sections = segment_sections(text)
    assert 'certifications' in sections and 'skills' in sections
    assert 'education' in sections and 'experience' in sections


def test_content_classifier_does_not_use_filename_as_the_only_signal():
    result = classify_document('my-certificate.pdf', 'This file contains a personal career summary and work experience for twelve years across several companies.')
    assert result['category'] == 'cv'
    unknown = classify_document('resume.pdf', 'Scanned page with no readable text')
    assert unknown['category'] == 'other'
    assert unknown['subcategory'] == 'unknown'


def test_document_classifier_identifies_degree_document():
    result = classify_document('random-upload.pdf', 'DEGREE CERTIFICATE\nMaster of Science in Computer Science\nExample University\n2012')
    assert result['category'] == 'education'
    assert result['subcategory'] == 'degree_certificate'
