package main;

func returnPointerToInt() *int{
    var a *int;
    return a;
};

func main(){
    var a int;
    var b int;
    var c [3]int;
    c[returnPointerToInt()] = 2;
    // print a, b, c[1];
};
