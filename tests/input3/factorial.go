package main;

func factorial(n int) int{
	if n < 0 {
		return 1;
	};
	return n * factorial(n-1);
};

func main(){
	var tenth_factorial int;
	tenth_factorial = factorial(10);
};
