// BubbleSort
package main;

func main(){
    var n int;
    scan n;
    var arr [100]int;
    for i:=0; i<n; i++{
        scan arr[i];
    };


    for i:=0; i<n; i++{
        for j:=0; j<n; j++{
            if (arr[i] < arr[j]){
                tmp := arr[i];
                arr[i] = arr[j];
                arr[j] = tmp;
            };
        };
    };

    for i:=0; i<n; i++{
        print arr[i];
    };
};
