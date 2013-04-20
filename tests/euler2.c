

int main()
{
  
  int a1 = 1, a2 = 1, a3 = 2, sum = 0;

  while (a3 < 4000000) {
    a3 = a1 + a2;
    sum += a3 * !(a3%2);
    a1 = a2;
    a2 = a3;
  }

  if(sum != 4613732){
    return 1;
  }

  return 0; 
  
}
