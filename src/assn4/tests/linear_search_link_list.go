package main;

type node struct{
	data int;
	next *(type node);
};

func main(){
	var list [10](type node);
	for i:=0;i<9;i++{
		var val int;
		scan val;
		list[i].data = val;
		list[i].next = &list[i+1];
	};
	
	var key int;
	scan key;

	for i:=0;i<10;i++{
		if list[i].data == key{
			print i;
			return;
		};
	};

	print "Not Found";
};