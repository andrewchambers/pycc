

struct foo {
    
    int x;
    int y;
    int z[6];

};


int main() {
    

    struct foo bar[10];
    
    for(int i = 0; i < 10 ; i++) {
        bar[i].x = 1;
        bar[i].y = 5;
        bar[i].z[2] = 10;
    }
    
    
    struct foo * p;
    
    
    
    if(bar[5].x != 1) {
        return 1;
    }
    
    if(bar[5].y != 5) {
        return 2;
    }
    
    if(bar[5].z[2] != 10) {
        return 3;
    }
    
    p = &bar[5];
    
    if(p->x != 1) {
        return 1;
    }
    
    if(p->y != 5) {
        return 2;
    }
    
    if(p->z[2] != 10) {
        return 3;
    }
    
    return 0;
}
