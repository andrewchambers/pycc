

int f1(){
    return 1;
}

int f2(int a, int b) {
    return (a + b) * 2;
}

int main() {
    
    return (f1() + f2(f1(),f1() + f1() + 3)) - 13;
}
