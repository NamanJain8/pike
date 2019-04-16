package main;

// output: 1 50 335 285 2470

func sum(a int) int{
    return a;
};

func sum(a int, b int) int{
    return a + b;
};

func sum(a int, b int, c int) int {
    return a + b + c;
};

func sum(a [100]int, n int) int {
    res := 0;
    for i := 0;i < n;i++ {
        res += a[i];
    };
    return res;
};

func main(){
    print sum(1);
    print sum (100, -50);
    print sum (300, 30, 5);
    
    var squares[100]int;
    for i := 0;i < 100;i++ {
        squares[i] = i*i;
    };
    
    firstTenSquares := sum(squares, 10);
    twentySquares := sum(squares, 20);
    
    print firstTenSquares, twentySquares;
};
