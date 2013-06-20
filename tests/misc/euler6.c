

int printf(char *, ...);


int main()
{
  int s1 = 0, s2 = 0, i;

  for (i = 1; i < 101; i++) {
    //printf("s1: %d s2: %d \n",s1,s2);
    s1 += i*i;
    s2 += i;
  }
  
  int result = s2*s2 - s1;
  
  //printf("result: %d\n",result);
  
  if(result != 25164150)
    return 1;
    
  return 0;
}
