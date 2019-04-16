package main;

func main(){
    var i int;
    var j int;
    i = 4;
    j = 2;
    i = i + j;
    j++;
    // i = i + j++ does not work in Go
    print i, j;
};
