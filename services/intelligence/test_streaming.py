from streaming import normalize_ollama_chunk


def test_ollama_stream_chunk_preserves_native_thinking_and_metrics() -> None:
    chunk = {
        "model": "qwen3:8b",
        "thinking": "inspect employment section",
        "response": "{\"employment\":[]}",
        "done": True,
        "done_reason": "stop",
        "total_duration": 123456789,
        "load_duration": 1234567,
        "prompt_eval_count": 42,
        "prompt_eval_duration": 2345678,
        "eval_count": 17,
        "eval_duration": 3456789,
    }
    normalized = normalize_ollama_chunk(chunk, "ollama", "qwen3:8b")
    assert normalized["type"] == "chunk"
    assert normalized["thinking"] == chunk["thinking"]
    assert normalized["response"] == chunk["response"]
    assert normalized["done_reason"] == "stop"
    assert normalized["total_duration"] == 123456789
    assert normalized["eval_count"] == 17


def test_ollama_stream_normalizer_does_not_invent_missing_metrics() -> None:
    normalized = normalize_ollama_chunk({"response": "x", "done": False}, "ollama", "gemma3:4b")
    assert normalized == {"type": "chunk", "provider": "ollama", "model": "gemma3:4b", "response": "x", "done": False}
