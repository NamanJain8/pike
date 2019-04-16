package main;

func sin(x float) float{
    y := x*0.0174;
    return y;
};

func cos(x float) float{
    t := sin(x);
    t = (1.0 - (t*t));
    return t;
};

func main(){
    x := 15.0;
    print sin(x), cos(x);
};
