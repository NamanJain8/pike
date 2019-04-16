package main;

func returnInt() int{
    return 1;
};

func main(){
    var a int;
    var b int;
    var c [3]int;
    a = 2;
    b = 5;
    *(&a) = b;
    c[returnInt()] = 4;
    print a, b, c[1];
};
