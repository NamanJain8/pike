package main;

type foo = int; // this is not a struct

func main() {
	var name string;
	var courseID int;
	var transcript [100]string;

	name = courseID; // [Error]
	name = transcript; // [Error]
	name = transcript[5]; // this would work :)

	var grade string = "B";
	grade++; // [Error] cannot increase grade that easily :P

	name, courseID = 335, "Compiler"; // int, string order reversed

	var size type foo;
	name = size.value; // foo is not a struct

	name + courseID; // cannot add string and int

	var shouldSleep, assignmentDone bool;
	shouldSleep + shouldSleep; // cannot add 2 binary number

	name = name + name; // this works just fine :)

	courseID && courseID; // In go we cannot use bitwise AND on integers

	notName := !name; // cannot do not on strings

	courseID += 100; // works fine

	courseID += name; // error since cannot be increment with string

	if "True" { // this should have been true instead of "True"
		// correct your code :P
	};

	for i := 1; "False"; i++ {
		// correct your code :P
	};
};