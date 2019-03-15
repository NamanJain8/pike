package main;


func main() {
	{
		a := 5;
	};
	b := a; // a does not exist in this scope

	break; // cannot write break anywhere, is should be in a for loop
	if true {
		break; // not even here
	}
	else {
		continue; // same goes for continue
	};

	for i := 1; i < 100; i++ {
		i += 1;
		break; // this works
		if true {
			continue; // this also works
		};
	};
};