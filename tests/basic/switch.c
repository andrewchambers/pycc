
void puts(char *);

int main() {
    
    int i;
    for(i = 0; i < 6; i++) {
        puts("start");
    
        switch(i) {
            case 0:
                puts("0");
            case 1:
                puts("1");
            case 2:
                puts("2");
            case 3:
                puts("3");
                break;
            case 4:
                continue;
            default:
                puts("default");
            case 10:
                puts("afterdefault");
        }
        
        
        puts("end");
    }
    
    return 0;
    
}


