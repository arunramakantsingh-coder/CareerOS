from app.core.security import create_access_token, decode_access_token, hash_password, verify_password

def test_password_hash_round_trip():
    password = "Strong-password-123!"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong-password", hashed)

def test_access_token_contains_identity_claims():
    token = create_access_token("user-id", "tenant-id")
    payload = decode_access_token(token)
    assert payload["sub"] == "user-id"
    assert payload["tenant_id"] == "tenant-id"
    assert "exp" in payload
