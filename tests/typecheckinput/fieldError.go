package main;

type person struct {
	name string;
	age int;
};

func main() {
	var folk, mob type person;

	folk.name = "Mohan";
	folk.age  = 22;
	mob 	  = folk.sex; // sex field is not present
};