from app.utils.document_intelligence import classify_document, segment_sections
from app.utils.cv_parser import CVParser


def test_cv_sections_are_segmented_without_cross_contamination():
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
    parsed = CVParser().parse(text)
    assert 'aws' not in [x['name'].lower() for x in parsed['certifications']]
    assert any('AWS Certified Solutions Architect' in x['name'] for x in parsed['certifications'])
    assert any('Master of Science' in x['degree'] for x in parsed['education'])
    assert not any('AWS' in x['degree'] for x in parsed['education'])
    assert any(x['name'] == 'AWS' for x in parsed['skills'])
    assert 'certifications' in sections and 'skills' in sections


def test_certification_document_can_produce_credential_but_not_education():
    text = '''CERTIFICATE OF COMPLETION
Certification: AWS Certified Solutions Architect - Associate
Issuer: Amazon Web Services
Credential ID: ABC123
Issued: 2025
'''
    parsed = CVParser().parse(text, document_category='certification')
    assert len(parsed['certifications']) == 1
    assert parsed['certifications'][0]['issuer'] == 'Amazon Web Services'
    assert parsed['education'] == []
    assert parsed['skills'] == []


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
