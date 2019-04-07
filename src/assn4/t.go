package main;

type foo = int;

type address [10](*(type foo));

func main() {
    var a type foo;
    var b type address;
};
