
PYTHON="python"

for TEST in `ls ./tests/*.c`
do
    #echo $TEST
    rm -f ./a.out
    gcc -std=c99 -m32 $TEST > /dev/null 2>&1
    
    timeout 3s ./a.out > /dev/null 2>&1
    
    if test $? -ne 0 
    then
        echo "test $TEST broken in gcc ... please fix"
        exit 1
    fi
    
    rm -f ./a.out
    $PYTHON cc.py $TEST --output out.s > /dev/null 2>&1 && gcc -m32 ./out.s > /dev/null 2>&1
    timeout 3s ./a.out > /dev/null 2>&1
    
    if test $? -ne 0 
    then
        echo "test $TEST broken without --iropt"
    fi
    
    
    rm -f ./a.out
    $PYTHON cc.py --iropt $TEST --output out.s  > /dev/null 2>&1 && gcc -m32 ./out.s > /dev/null 2>&1
    timeout 3s ./a.out > /dev/null 2>&1
    if test $? -ne 0 
    then
        echo "test $TEST broken with --iropt"
    fi
    
done
