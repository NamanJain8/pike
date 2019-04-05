package main;

func fib(n int) int{
	if n < 1 {
		return 1;
	};
	return fib(n-1) + fib(n-2);
};

func main(){
	tenth_fibonacci := fib(10);
};
