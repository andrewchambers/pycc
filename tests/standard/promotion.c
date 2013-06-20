

void printf(char *, ...);


int main() {
    
    char a;
    char b;
    char c;
    
    a = 0xff;
    b = '\x02';
    
    c = (a * b) >> 1;
    
    printf("%X\n",(int)c);
    printf("%X\n",(unsigned int)c);
    printf("%X\n",(unsigned char)c);
    printf("%X\n",(unsigned int)(unsigned char)c);

}
