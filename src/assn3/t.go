package main;
import "fmt";

type person struct {
	age bool;
	sex int;
	name string;
};

type x=int;

func main() {
	type x=float;
	var p type person;
	var b, c int;
	if true {
		var a int;
		a = 10;
		if false{
			var b bool;
			b = false;
		}
		else{
			a = 10;
			var a int;
		};
	};
};

