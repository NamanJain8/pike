package main;

type foo = int;

type address [10](*(type foo));

func main() {
	var hostels type address;
	var marks type foo;
	marks = (1 + 2 + 3 * 5);
};
