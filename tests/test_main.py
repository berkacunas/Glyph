def test_basic_math():
    """
    Bu test sadece test altyapısının çalıştığını doğrular.
    """
    assert 1 + 1 == 2

def test_string_operation():
    """
    Basit bir string testi.
    """
    word = "Glyph"
    assert word.upper() == "GLYPH"