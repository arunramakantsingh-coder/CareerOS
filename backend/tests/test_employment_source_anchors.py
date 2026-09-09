from app.intelligence.identity_reconciliation import _extract_source_employment_anchors


CV_WORK_HISTORY = """WORK EXPERIENCE
SR. CYBER SECURITY ARCHITECT | COGNIZANT (CLIENT: ALLIANZ GROUP)
Aug 2025 – Present
● Leading global firewall governance.
SENIOR NETWORK & SECURITY ARCHITECT | RANDSTAD (CLIENT: L'ORÉAL)
Mar 2024 – Jul 2025
● Architected migration from FortiWeb AWS to Cloudflare.
SENIOR NETWORK & SECURITY ARCHITECT – CONSULTANT TO CIO | BURGAN BANK
Nov 2021 – Jan 2024
● Designed enterprise IAM.
SENIOR MANAGER – NETWORK & TELECOMMUNICATION | CBI BANK (UAE)
Aug 2018 – Mar 2020
SENIOR NETWORK & SECURITY ARCHITECT – CONSULTANT | CBI BANK
Jul 2016 – Jul 2018
● Directed core network modernization.
EDUCATION
Bachelor of Business Administration
"""


def test_source_employment_anchors_ignore_competencies_and_parse_clients():
    anchors = _extract_source_employment_anchors(CV_WORK_HISTORY)
    assert [(x["organization"], x["title"], x["client"]) for x in anchors] == [
        ("COGNIZANT", "SR. CYBER SECURITY ARCHITECT", "ALLIANZ GROUP"),
        ("RANDSTAD", "SENIOR NETWORK & SECURITY ARCHITECT", "L'ORÉAL"),
        ("BURGAN BANK", "SENIOR NETWORK & SECURITY ARCHITECT – CONSULTANT TO CIO", None),
        ("CBI BANK (UAE)", "SENIOR MANAGER – NETWORK & TELECOMMUNICATION", None),
        ("CBI BANK", "SENIOR NETWORK & SECURITY ARCHITECT – CONSULTANT", None),
    ]
    assert anchors[0]["start_date"] == "2025-08-01"
    assert anchors[0]["end_date"] is None
    assert anchors[0]["is_current"] is True
    assert anchors[1]["start_date"] == "2024-03-01"
    assert anchors[1]["end_date"] == "2025-07-01"
    assert "global firewall governance" in anchors[0]["responsibilities"][0].lower()
