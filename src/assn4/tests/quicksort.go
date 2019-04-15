// QuickSort
package main;

var arr [6]int;
// {1, 74, 37, 19, 6};


func partition (low int, high int) int{
	var pivot int = arr[high];
	var i int = (low - 1);

	for j := low; j <= high- 1; j++{
		if arr[j] <= pivot{
			i++;
            tmp := arr[i];
            arr[i] = arr[j];
            arr[j] = tmp;
		};
	};
    tmp2 := arr[i+1];
    arr[i+1] = arr[high];
    arr[high] = tmp2;
    return (i + 1);
};

func quickSort(low int, high int){
	if low < high{
		var pi int;
        pi = partition(low, high);

		quickSort(low, pi - 1);
		quickSort(pi + 1, high);
	};
};

func main()
{
    // arr[0] = 1;
    // arr[1] = 74;
    // arr[2] = 37;
    // arr[3] = 19;
    // arr[4] = 6;
    // arr[5] = 23;

    for i:=0; i<6; i++{
        scan arr[i];
    };

	var n int = 6;
	quickSort(0, n-1);
};
