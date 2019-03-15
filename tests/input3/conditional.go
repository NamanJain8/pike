package main;

func main() {
	p := 57;
	divisor := 0;
	defaultMsg := "57 is prime";
	for i := 1; i < p;i++ {
		rem := p % i;
		if rem == 0 {
			divisor += 1;
		};
	};
	msg := "This variable will be printed to screen";
	if divisor == 0 {
		msg = defaultMsg;
	}
	else {
		msg = "57 is not prime, it has ";
		msg = msg + (typecast string(divisor));
		msg = msg + " divisor/s";
	};
};