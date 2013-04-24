

int main()
{
  int s1 = 0, s2 = 0, i;

  for (i = 1; i < 101; i++) {
    s1 += i*i;
    s2 += i;
  }
  if(s2*s2 - s1 != 25164150)
    return 1;
    
  return 0;
}
