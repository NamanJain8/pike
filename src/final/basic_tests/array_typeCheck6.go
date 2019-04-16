// Not Working

package main;

type s struct {
	a int;
	b [5][5]int;
};

type t struct {
	x [10]type s;
};

func f(a [5]*int, b [5][5]int){
    b[1][2] = 10;
};

func main(){
    var a [10][10]int;
    var b [10][10]int;
    var c [5]*int;
    var y type t;
    var i int;
    var fp *float;
    y.x[3].b[1][2] = 5;
    f(c, y.x[3].b);
    print y.x[3].b[1][2];
};
