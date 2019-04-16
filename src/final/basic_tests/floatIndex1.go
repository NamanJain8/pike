package main;

func returnFloat() float{
    return 2.4;
};

func main(){
    var a int;
    var b int;
    var c [3]int;
    c[returnFloat()] = 4;
    print a, b, c[1];
};
