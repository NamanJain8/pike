// DirectedGraphAdjacencyList
//  Incomplete
package main;

type node struct{
	val int;
	next *(type node);
};

func main(){
    n := 6;
    var edges [5][2]int;
    var adjList [6]*type node;

    for i:=0; i<n; i++{
        scan edges[i][0], edges[i][1];
        var new type node;
        new.val = edges[i][1];
        // new.next = nil;
        var head *type node = adjList[edges[i][0]];
        for{
            // if (*head).next == nil{
            //     break;
            // };
            head = (*head).next;
        };
        (*head).next = &new;
    };

};

// Error Msg: [TypeMismatch]: ['pointer',
// ['struct', {'val': {'type': ['int'], 'size': 4, 'offset': 0}, 'next': {'type': ['pointer', ['struct', 'node']], 'size': 4, 'offset': 4}}]]
// assigned to ['pointer', ['struct', 'node']] (line: 25)

// Node vs Definition of node
