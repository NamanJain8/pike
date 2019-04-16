package main;

func p(a string) int{
    print 99;
    return 1;
};

func p(a int, b int) int{
    print a+b+20;
    return 10;
};


func main(){
    a := 1;

    print p(a, a);

    tmp := "hello";

    print p(tmp);
};
