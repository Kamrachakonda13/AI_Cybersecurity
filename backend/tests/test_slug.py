from app.services.slug import slugify


def test_slug_collapses_specials():
    assert slugify("Weights & Biases Weave") == "weights-biases-weave"
    assert slugify("A  B") == "a-b"
    assert slugify("---x---") == "x"
    assert slugify("") == ""
    assert slugify("tool.name") == "tool-name"
    assert slugify("tool_name") == "tool-name"


def test_slug_no_ampersand_or_slash_or_double_hyphen():
    for s in ["a&b", "a/b", "a\\b", "a b", "a---b", "a+++b", "a (b) c"]:
        out = slugify(s)
        assert "&" not in out
        assert "/" not in out
        assert "\\" not in out
        assert " " not in out
        assert "---" not in out
