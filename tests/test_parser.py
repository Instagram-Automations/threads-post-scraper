from src.parser import ThreadsParser


def test_parser_normalizes_records():
    raw = [
        {"username": "u", "post_id": 1, "content": " hi ", "likes": "3", "comments": None, "hashtags": ["a", "b"], "mentions": []}
    ]
    parsed = ThreadsParser().parse_posts(raw)
    assert parsed and parsed[0]["post_id"] == "1"
    assert parsed[0]["content"] == "hi"
    assert parsed[0]["likes"] == 3
    assert parsed[0]["comments"] == 0
