



typedef int foo;

typedef struct {
    int x;
} foobar;


int main() {
    
    foo x = 0;
    foobar y;
    y.x = 5; 
    return x + y.x;
    
}
