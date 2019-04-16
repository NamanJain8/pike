package main;

type s struct {
	b int;
	a int;
};

type t struct {
	b int;
	a int;
};

func g(x int, y int){
    print x;
    print y;
};

func main(){
    var x type s;
    var y type t;
    var q int;
    x.b = 2;
    y = x;
    x.b = 4;
    print x.b, y.b;
};
