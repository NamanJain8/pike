// 7plusArguements
package main;

// Output: 10 55

func manyVariables(a int, b int, c int, d int, e int, f int, g int, h int, i int, j int) int{
    return a+b+c+d+e+f+g+h+i+j;
};

func main(){
    print manyVariables(1, 1, 1, 1, 1, 1, 1, 1, 1, 1);
    print manyVariables(1, 2, 3, 4, 5, 6, 7, 8, 9, 10);
};
