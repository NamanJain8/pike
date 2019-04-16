package main;

type hello struct {
	b float;
	a int;
};

type hello_world struct {
	b float;
	a int;
};

func get_a(k type hello) int{
    return k.a;
};

func main(){
    var b int;
    var a int;
    var k type hello;
    a = get_a(k);
};
