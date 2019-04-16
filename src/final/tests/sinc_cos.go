package main;

func sin(x float) float{
    x = x*0.0174;
    y := ((x) - ((x*x)/6.0) + ((x*x*x*x*x)/120.0));
    return y;
};

func cos(x float) float{
    t := sin(x);
    t = (1.0 - (t*t));
    return t;
};

func main(){
    x := 30.0;
    print sin(x);
    print cos(x);
};
