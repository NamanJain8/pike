// MutualRecursion
package main;

func odd(n int) int {
    if n==0{
        return 0;
    };
    return even(n-1);
};

func even(n int) int {
    if n==0{
        return 1;
    };
    return odd(n-1);
};

func main() {
    var oddev [2]string;
    oddev[0] = "odd";
    oddev[1] = "even";
    for i := 0; i < 20; i++ {
        print i, " is ", oddev[even(i)];
    };
};
