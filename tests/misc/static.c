

int printf(char *,...);


void foo() {
    static int x = 3;
    x++;
    printf("%d\n",x);
    x++;
}



int main() {
    foo();
    foo();
    foo();
    return 0;
}
