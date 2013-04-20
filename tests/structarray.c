

struct foo {
    
    int x;
    int y;
    int z;

};


int main() {
    
    struct foo bar[10];
    
    for(int i = 0; i < 10 ; i++) {
        bar[i].x = 1;
        bar[i].y = 5;
        bar[i].z = 10;
    }
    
    
    struct foo * p;
    
    p = &bar[5];
    
    if(p->x != 1) {
        return 1;
    }
    
    if(p->y != 5) {
        return 2;
    }
    
    if(p->z != 10) {
        return 3;
    }
    
    return 0;
}
