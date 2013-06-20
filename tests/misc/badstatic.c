

int printf(char *,...);


void foo(int arg) {

    static int x = arg;
    x++;
    printf("%d\n",x);
    x++;
}



int main() {
    foo(1);
    foo(2);
    foo(3);
    return 0;
}
