

int main(){
    
    int x = 0;
    
    start:
    
    if(x){
        goto exit;
    } else {
        x = 1;
        goto start;
    }
    
    exit:
    
    return 5;

}
