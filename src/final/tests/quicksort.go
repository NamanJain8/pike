// QuickSort
package main;

func quickSort(arr [100]int, l int, h int) [100]int{
	var stack [100]int;
	capacity := h-l+1;
	top := -1;

	top++;
	stack[top] = l;
	top++;
	stack[top] = h;

	for ;top>=0;{
		h = stack[top];
		top--;
		l = stack[top];
		top--;

		// Partition starts
		x := arr[h];
		i := l-1;

		for j:=l;j<=(h-1);j++{
			if arr[j] <= x{
				i++;
				tmp := arr[i];
				arr[i] = arr[j];
				arr[j] = tmp;
			};
		};
		tmp := arr[i+1];
		arr[i+1] = arr[h];
		arr[h] = tmp;
		// Partition ends

		p := i+1;
		if (p-1) > l {
			top++;
			stack[top] = l;
			top++;
			stack[top] = p-1;
		};

		if (p+1)<h{
			top++;
			stack[top] = p+1;
			top++;
			stack[top] = h;
		};
	};
	return arr;
};

func main()
{
	var n int;
	var arr [100]int;
	scan n;

	for i:=0; i<n; i++{
		scan arr[i];
	};

	arr = quickSort(arr, 0, n-1);

	for i:=0; i<n; i++{
        print arr[i];
    };
};

