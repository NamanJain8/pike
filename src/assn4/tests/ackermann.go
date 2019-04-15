// Ackermann
package main;

type pair struct {
	a, b int;
};

// var (
// 	lookupTable = make(map[pair]int);
// );

func ackermann(m int, n int) int {
    var k type pair;
    k.a = m;
    k.b = n;
    ans := lookupTable[k][0];
    ok := lookupTable[k][1];
    if ok == true {
		return ans;
	};
	if m == 0 {
		ans = n + 1;
	} else if n == 0 {
		ans = ackermann(m-1, 1);
	} else {
		ans = ackermann(m-1, ackermann(m, n-1));
	};
    lookupTable[k] = ans;
	return ans;
};

func main() {
	for i := 0; i < 6; i++ {
		for j := 0; j < 6; j++ {
			ans := ackermann(i, j);
			print "Calculated ackermann(", i, ", ", j, ") = ", ans;
		};
	};
};
