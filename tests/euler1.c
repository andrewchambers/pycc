

int 
main ()
{
    int i;
    int sum = 0;
    
    for(i = 1; i < 1000 ; i++ ) {
        if(i % 3 == 0) {
            sum += i;
        } else if ( i % 5 == 0) {
            sum += i;
        }
    }
    
    if( sum == 233168) {
        return 0;
    }
    
    return 1;
}
