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

def test_charparse():

    tests = [
                (r"'a'",ord('a')),
                (r"'\n'",ord('\n')),
                (r"'\x00'", 0),
                (r"'\xff'",255),
            ]
    for s,parsed in tests:
        assert cstrings.parseCChar(s) == parsed
