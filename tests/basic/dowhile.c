
void puts(char *);

int main() {
    
    int x = 0;
    
    do {
        puts("Hello!");
        x = x + 1;
    } while(x < 5);
    
    x = 0;
    
    do {
        puts("a!");
        x = x + 1;
        continue;
        puts("b!");
    } while(x < 5);
    
    do {
        puts("x!");
        x = x + 1;
        break;
        puts("y!");
    } while(x < 5);
    

}


