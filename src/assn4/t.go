package main;

type node struct {
    a int;
    b string;
    next *(type node);
};

func main() {
    var listHead, n1, n2 (type node);
    listHead.next = &n1;
    n1.next = &n2;
};
