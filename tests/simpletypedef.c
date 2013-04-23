

typedef struct _foo {
    
    int x;
    int y;
    
} foo;

typedef foo foofoo;


int main() {
    
    foo bar;
    
    foofoo barbar;
    
    bar.x = 3;
    bar.y = 3;
    
    barbar.x = 3;
    barbar.y = 3;
    
    
    
    return bar.x + bar.y - barbar.y - barbar.y;
}
