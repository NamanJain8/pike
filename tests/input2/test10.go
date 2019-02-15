// Binary Search Algorithm in GoLang

package main;

import (
	"fmt";
);

func BinarySearch(target_map int, value int) int {

	start_index := 0;
	end_index := len(target_map) - 1;

	for start_index <= end_index {

		median := (start_index + end_index) / 2;

		if target_map[median] < value {
			start_index = median + 1;
		} else {
			end_index = median - 1;
		};

	};

	if start_index == len(target_map) || target_map[start_index] != value {
		return -1;
	} else {
		return start_index;
	};

};

func main() {

    var a [7]int;
    a[1] = 1;
    a[2] = 2;
    a[3] = 3;
    a[4] = 4;
    a[5] = 5;
    a[6] = 6;
    a[7] = 7;

	fmt.Println(BinarySearch(a, 5));

};
