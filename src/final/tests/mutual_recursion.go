// MutualRecursion
package main;

func even(n int) int;

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
    var oddev [2]int;
    oddev[0] = 1;
    oddev[1] = 0;
    for i := 0; i < 20; i++ {
        print i, oddev[even(i)];
    };
};
