import cstrings


def test_stringparse():
    
    tests = [
                (r'','\x00'),
                (r'"\n"','\n\x00'),
                (r'"\r"','\r\x00'),
                (r'"\x03"','\x03\x00'),
                (r'"\\\r\n\""','\\\r\n"\x00'),
                (r'"hello..."','hello...\x00'),
             ]
    for s,parsed in tests:
        assert cstrings.parseCString(s) == parsed


