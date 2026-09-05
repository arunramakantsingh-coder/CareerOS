from app.utils.document_intelligence import classify_document, segment_sections
from app.utils.cv_parser_v3 import CVParser


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


def test_employment_is_date_anchored_and_extracts_company_title_and_responsibilities():
    text = '''EXPERIENCE

Network & Security Architect Consultant to CIO | CBI
Mar 2020 - Aug 2022 (UAE)
• Led vendor and partner governance across network and security services.
• Delivered SD-WAN and Zero Trust transformation.

Enterprise Technology Manager | Acme Technologies Ltd
Jan 2018 - Feb 2020
• Managed service lifecycle architecture and operational metrics.
'''
    parsed = CVParser().parse(text)
    assert len(parsed['professional']) == 2
    first = parsed['professional'][0]
    assert first['company'] == 'CBI'
    assert 'Architect' in first['title']
    assert first['start_date'] == '2020-03-01'
    assert first['end_date'] == '2022-08-31'
    assert first['location'] == 'UAE'
    assert any('vendor and partner governance' in x.lower() for x in first['responsibilities'])
    second = parsed['professional'][1]
    assert second['company'] == 'Acme Technologies Ltd'
    assert second['title'] == 'Enterprise Technology Manager'
    assert second['start_date'] == '2018-01-01'
    assert second['end_date'] == '2020-02-29'


def test_employment_can_recover_header_near_both_sides_of_ocr_date_line():
    text = '''EXPERIENCE

CBI
Network & Security Architect Consultant to CIO
Mar 2020 S · (UAE) Aug 2022
Led vendor and partner governance across network and security services.
'''
    parsed = CVParser().parse(text)
    assert len(parsed['professional']) == 1
    item = parsed['professional'][0]
    assert item['company'] == 'CBI'
    assert 'Architect' in item['title']
    assert item['start_date'] == '2020-03-01'
    assert item['end_date'] == '2022-08-31'
    assert item['location'] == 'UAE'


def test_competency_bullets_are_not_employment_records():
    text = '''EXPERIENCE
Vendor/Partner Governance | Program Leadership | Service Delivery Alignment
SDN/ACI | SD-WAN | Multi-Vendor Firewalls | Load Balancing | Segmentation
Service Lifecycle Architecture | SLA/OLA Design | Operational Metrics
'''
    parsed = CVParser().parse(text)
    assert parsed['professional'] == []


def test_incomplete_role_near_a_date_is_not_persisted_as_fake_employment():
    text = '''EXPERIENCE
B · CIO
2020 - 2022
Vendor/Partner Governance | Program Leadership | Service Delivery Alignment
'''
    parsed = CVParser().parse(text)
    assert parsed['professional'] == []


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
    result = classify_document('my-certificate.pdf', 'This file contains a personal career summary and work experience for twelve years across several companies. Education and Skills are also listed.')
    assert result['category'] == 'cv'
    misleading = classify_document('Pan Card.pdf', 'Professional summary\n15 years of network and security leadership\nEXPERIENCE\nEducation\nSkills')
    assert misleading['category'] == 'cv'
    unknown = classify_document('resume.pdf', 'Scanned page with no readable text')
    assert unknown['category'] == 'other'
    assert unknown['subcategory'] == 'unknown'


def test_document_classifier_identifies_degree_document():
    result = classify_document('random-upload.pdf', 'DEGREE CERTIFICATE\nMaster of Science in Computer Science\nExample University\n2012')
    assert result['category'] == 'education'
    assert result['subcategory'] == 'degree_certificate'


def test_document_classifier_identifies_pan_card_from_content_even_with_ocr_spacing():
    result = classify_document('random-upload.pdf', 'INCOME TAX DEPARTMENT\nGOVT. OF INDIA\nPERMANENT ACCOUNT NUMBER\nABCDE 1234 F')
    assert result['category'] == 'identity'
    assert result['subcategory'] == 'pan_card'


def test_document_classifier_identifies_aadhaar_from_content():
    result = classify_document('renamed-file.pdf', 'Unique Identification Authority of India\nAadhaar\nGovernment of India\nXXXX XXXX 1234')
    assert result['category'] == 'identity'
    assert result['subcategory'] == 'aadhaar_card'


def test_document_classifier_identifies_offer_from_content_even_when_filename_is_generic():
    result = classify_document('scan-001.pdf', 'We are pleased to offer you employment. Your date of joining will be 15 March 2024. Terms of employment and place of posting are enclosed.')
    assert result['category'] == 'employment'
    assert result['subcategory'] == 'offer_letter'
