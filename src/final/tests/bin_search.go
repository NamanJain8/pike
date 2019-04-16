package main;

func bin_search(arr [100]int, len int, key int) int{
	first := 0;
	last := len - 1;

	for ;first<=last;{
		middle := first+(last - first)/2;
		if arr[middle] == key{
			return middle+1;
		};
		if arr[middle] < key{
			first = middle + 1;
		}
		else{
			last = middle-1;
		};
	};
	return -1;
};

func main(){
	var a [100]int;
	var n, key int;
	scan n;
	scan key;
	for i:=0;i<n;i++{
		scan a[i];
	};
	idx := bin_search(a, n, key);
	print idx;
};