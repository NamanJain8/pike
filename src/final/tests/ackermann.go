package main;

func Ackermann(m int, n int) int {
    if m == 0 {
        return n+1;
    };
    if (m > 0) && (n == 0) {
        return Ackermann(m-1, 1);
    };
    return Ackermann(m-1, Ackermann(m, n-1));
};

func main(){
    print Ackermann(3, 2);
};
