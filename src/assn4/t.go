package main;

func p(a int) int {
    return 1;
};

func p(a string) int {
    return -1;
};

func p(b int) int {
    return 10;
};

func main() {
    tmp := "hello";
    p(tmp);
    a := 1;

    p(a);
};
