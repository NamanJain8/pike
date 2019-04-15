// Fibonacci
package main;

// func fib(n int) int{
// 	if n < 1 {
// 		return 1;
// 	};
// 	return fib(n-1) + fib(n-2);
// };

func fib(n int) int {
	var result int;
    first := 0;
    second := 1;
	for i := 0; i <= n; i = i+1 {
		if i == n {
			result = first;
		};
        first = first + second;
        second = first;
	};
	return result;
};

func main(){
    for i := 0; i <= 10; i++ {
            print "fib(", i, ") = ", fib(i);
    };
};
