

struct foo {
    
    int x;
    int y;
    int z;

};



int main() {
    
    struct foo bar;
    
    struct foo * p;
    
    
    bar.x = 2;
    
    bar.y = 3;
    
    p = &bar;
    
    p->z = 1;

    return bar.y - bar.x - bar.z;
}
