
void printf(char *,...);
void puts(char *);

int main() {
   int x;
   
   x = (puts("foo"),3);
   printf("%d\n",x);
}
