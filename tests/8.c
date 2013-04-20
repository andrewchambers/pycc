//EXPECTED FAIL

int foo(int a) {
    return a - 5;
}

int 
main ()
{
    return foo(5);
}
