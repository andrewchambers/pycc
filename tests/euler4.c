

int is_palindromic(int n)
{
  int reversed = 0, t = n;

  while (t) {
    reversed = 10*reversed + (t % 10);
    t /= 10;
  }
  return reversed == n;
}


int main()
{
  int i, j, max = 0;
  for (i = 100; i < 1000; i++) {
    for (j = 100; j < 1000; j++) {
      int p = i*j;
      if (is_palindromic(p) && p > max ) {
        max = p;
      }
    }
  }
  
  
  if(max != 906609)
    return 1;
  
  return 0;
}


