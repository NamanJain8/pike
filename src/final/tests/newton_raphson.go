package main;

func foo(x float) float{
        return (((x*x*x) - (x*x)) + (3.0));
};

func derivFunc(x float) float{
        return (((3.0)*x*x) - ((2.0)*x));
};

func abs(x float) float{
        if x < (0.0) {
                return (-x);
        }
        else{
                return x;
        };
};

func NR(x float) float{
        h := (foo(x) / derivFunc(x));
    for i:=0;i<50;i++ {
                h = (foo(x)/ derivFunc(x));
        // print abs(h);
        x = x - h;
        };
        return x;
};

func main(){
        var x0 float;
        // scan x0;
    x0 = 2.0;
    y0 := 3.0;
        ans := NR(x0);
        print ans;
        // return;
};
