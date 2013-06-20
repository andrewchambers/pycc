
int 
main ()
{
    
    int counter = 0;
    
    again:
    
    for(;;) {
        
        outerloop:
        
        if (counter == 1000) {
            counter = 50;
            break;
        }
        
        for(;;)  {
            counter += 1;
            if(counter == 1000) {
                goto outerloop;
            }
        }
        
    }
    
    return counter - 50;
}
