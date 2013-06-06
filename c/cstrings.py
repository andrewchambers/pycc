





def parseCString(rawString):
    trimmed = rawString[1:-1]
    result = ''
    
    length = len(trimmed)
    
    idx = 0
    while idx < length:
        if trimmed[idx] == '\\':
            idx += 1
            if trimmed[idx] == 'n':
                result += '\n'
            elif trimmed[idx] == 'r':
                result += '\r'
            elif trimmed[idx] == '\\':
                result += '\\'
            elif trimmed[idx] == 'x':
                result += chr(int(trimmed[idx+1:idx+3],16))
                idx += 2
            else:
                result += trimmed[idx]
        else:
            print trimmed[idx]
            result += trimmed[idx]    
        
        idx += 1        
        
    result += '\x00'
    return result

def parseCChar(rawString):
    s = parseCString(rawString)
    return ord(s[0])
