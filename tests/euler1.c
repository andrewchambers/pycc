

int 
main ()
{
    int i,y;
    int sum = 0;
    
    for(i = 0; i < 10000 ; i++ ) {
        for(y = 0; y < 10000 ; y++ ) {
            if(i % 3 == 0) {
                sum += i;
            } else if ( i % 5 == 0) {
                sum += i;
            }
        }
    }
    
    if( sum == 233168) {
        return 0;
    }
    
    return 1;
}
