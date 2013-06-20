

int main() {
    
    int arr[10][10];
    
    
    for(int i = 0; i < 10 ; i++) {
        for(int j = 0 ; j < 10; j++) {
            arr[i][j] = i * j;
        }
    }
    
    for(int i = 0; i < 10; i++) {
        if(arr[0][i] != 0) {
            return 1;
        }
    }
    
    for(int i = 0; i < 10; i++) {
        if(arr[i][0] != 0) {
            return 2;
        }
    }

    for(int i = 0; i < 10; i++) {
        if(arr[5][i] != i * 5) {
            return 3;
        }
    }
    
    return 0;
    
}
