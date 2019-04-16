// Not Working

package main;

type node struct {
	val int;
	next *(type node);
};

func main(){
    var root [100](type node);
    var n int;
    var v int;
    scan n;
    for i := 0;i < n;i++ {
        scan root[i].val;
        root[i].next = &(root[i+1]);
    };

    var key int;
    scan key;

    var head (type node);
    head = (root[0]);

    for i := 0;i < n;i++ {
        if head.val == key {
            print i;
        };
        head = *(head.next);
    };
};
