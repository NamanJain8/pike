package main;

func foo(x float) float{
	return x*x*x - x*x + 3.0;
};

func derivFunc(x float) float{
	return 3.0*x*x - 2.0*x;
};

func abs(x float) float{
	if x < 0.0 {
		return -x;
	}
	else{
		return x;
	};
};

func NR(x float) float{
	h := foo(x) / derivFunc(x);
	for abs(h) >= 0.001{
		h = foo(x)/ derivFunc(x);
		x = x - h;
	};
	return x;
};

func main(){
	var x0 float;
	scan x0;
	ans := NR(x0);
	print ans;
	return;
};