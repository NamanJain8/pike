package main;

type node struct{
	val int;
    num_child int;
	child [100]*(type node);
};

func main(){
    var n, m int;
    scan n, m;
    var nodes[100] (type node);
    
    for i:=0;i<n;i++{
        nodes[i].num_child = 0;
    };

    for i:=0;i<n;i++{
        nodes[i].val = i;
    };

    for i:=0; i<m; i++{
        var a, b int;
        scan a, b;

        nodes[a].child[nodes[a].num_child] = &nodes[b];
        nodes[a].num_child++;
        nodes[b].child[nodes[b].num_child] = &nodes[a];

        nodes[b].num_child++;
    };

    for i:=0;i<n;i++{
        print nodes[i].val;
        for j:=0;j<nodes[i].num_child;j++{
            var temp type node;
            temp = *(nodes[i].child[j]);
            print temp.val;
        };
    };

};
