from app.intelligence.retrieval import _excerpt, _score, _tokens


def test_retrieval_tokens_remove_common_noise():
    tokens = _tokens("Tell me about my cloud security experience")
    assert "cloud" in tokens
    assert "security" in tokens
    assert "about" not in tokens
    assert "experience" not in tokens


def test_retrieval_score_rewards_query_overlap():
    query = _tokens("cloud security architecture")
    strong = _score(query, "Enterprise cloud security architecture and governance")
    weak = _score(query, "Education history and certifications")
    assert strong > weak
    assert strong > 0


def test_excerpt_focuses_on_matching_region_for_long_content():
    query = _tokens("terraform")
    text = "Introductory career information. " * 40 + "Designed Terraform automation for multi-cloud deployments. " + "Closing notes. " * 20
    excerpt = _excerpt(text, query, limit=250)
    assert "Terraform" in excerpt
    assert len(excerpt) <= 252
