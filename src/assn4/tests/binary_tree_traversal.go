// Not Working

package main;

type node struct {
	val int;
	left *(type node);
    right *(type node);
    isLeaf int;
};

/*
            0
        1       2
    3      4  5   6
  7   8         9   10 
*/

func dfs(nd type node) int {
    print nd.val;

    if (nd.isLeaf) == 1 {
        return 0;
    };
    l := *(nd.left);
    r := *(nd.right);
    dfs(l);
    dfs(r);
    return 0;
};

func main(){
    var tree [100](type node);
    n := 11;

    for i := 0;i < n;i++ {
        tree[i].val = i;
        tree[i].isLeaf = 0;
    };


    tree[4].isLeaf = 1;
    tree[5].isLeaf = 1;
    tree[7].isLeaf = 1;
    tree[8].isLeaf = 1;
    tree[9].isLeaf = 1;
    tree[10].isLeaf = 1;

    tree[0].left = &tree[1];
    tree[0].right = &tree[2];

    tree[1].left = &tree[3];
    tree[1].right = &tree[4];

    tree[2].left = &tree[5];
    tree[2].right = &tree[6];

    tree[3].left = &tree[7];
    tree[3].right = &tree[8];

    tree[6].left = &tree[9];
    tree[6].right = &tree[10];
    
    root := tree[0];

    dfs(root);
};
