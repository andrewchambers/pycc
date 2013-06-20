

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
    if(is_palindromic(8555548)) {
        return 1;
    }
    return !is_palindromic(855558);
}


