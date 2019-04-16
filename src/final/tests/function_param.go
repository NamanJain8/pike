// QuickSort
package main;

type marks struct {
    cs335 int;
    cs315 int;
    cs300 int;
};

// returning array from function
func getSqArr() [100]int {
    var arr [100]int;
    for i := 0;i < 100;i++ {
        arr[i] = i*i;
    };
    return arr;
};

// passing an array to a function
func printArr(a [100]int, n int) int {
    for i := 0;i < n;i++ {
        print a[i];
    };
    return 1;
};

// return an struct from a function
func getMarks() type marks {
    var m type marks;
    m.cs335 = 100;
    m.cs315 = 99;
    m.cs300 = 98;
    return m;
};

// passing struct to a function
func printMarks(m type marks) int {
    print m.cs335, m.cs315, m.cs300;
    return 0;
};


func main() {
    sqArr := getSqArr();
    printArr(sqArr, 10);

    myMarks := getMarks();
    printMarks(myMarks);
};
