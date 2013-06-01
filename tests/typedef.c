



typedef struct {
    int x;
} foo;


typedef struct _bar {
    int y;
} bar;


int main() {
    
    bar x;
    struct _bar y;
    foo z;
    
    
    x.y = 0;
    y.y = 1;
    z.x = 2;
    
    
    
    return x.y + y.y + z.x;
    
}
