
void printf(char *,...);


int main() {
    int i;
    
    for(i = 0; i < 1000; i++) {
        printf("%d\n",i);
        
        if(i == 5) {
            i += 2;
            continue;
        }
        
        if(i == 15) {
            break;
        }
    }
    
    
}
