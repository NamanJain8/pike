package main;

type person struct {
	name string;
	sex  bool;
};

type person struct {
	name string;
	age int;
};

type person = string;

const ClassStrength int = 105;

const ClassStrength bool = false;

func main() {
	var a int;

	var a string;

	var b bool;

	b := false; // [Error] it should be b = false
};
