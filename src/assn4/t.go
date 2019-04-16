// 7plusArguements
package main;


type node struct {
    data int;
    next *(type node);
};


func main(){
    var x,y,z type node;
    y.data = 20;
    x.data = 10;
    z.data = 30;
    x.next = &y;
    y.next = &z;
    z.next = &x;
    print (*(x.next)).data, (*(y.next)).data, (*(z.next)).data;
};
