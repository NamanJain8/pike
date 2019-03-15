package main;

type student struct {
	name string;
	age  int;
	dept string;
};

type foo = bool;

func main() {
	var student1 type student;
	student1.name = "Raman";

	var student2 type deadInside; // [Error]
};
