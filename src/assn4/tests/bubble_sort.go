// BubbleSort
package main;

func bubblesort(items [5]int, len int) int{
    var n = len;
    var sorted = false;

    for !sorted {
        swapped := false;
        for i := 0; i < n-1; i++ {
            if items[i] > items[i+1] {
                tmp := items[i+1];
                items[i+1] = items[i];
                items[i] = tmp;
                swapped = true;
            };
        };
        if swapped == false {
            sorted = true;
        };
        n = n - 1;
    };
};

func main(){
    var arr [5]int;
    // {1, 74, 37, 19, 6};
    for i:=0; i<5; i++{
        scan arr[i];
    };

    print "Unsorted Array:";
    for i:=0; i<5; i++{
        print arr[i];
    };

    bubblesort(arr, 5);

    print "Sorted Array:";
    for i:=0; i<5; i++{
        print arr[i];
    };
};
