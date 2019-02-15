// Go's _structs_ are typed collections of fields.
// They're useful for grouping data together to form
// records.

package main;

import "fmt";

// This `person` struct type has `name` and `age` fields.
type person struct {
    name string;
    age  int;
};

func main() {

    s :=  typecast type MyFloat(a);
    s.age = 50;
    s.name = "Sean";
    // Access struct fields with a dot.
    fmt.Println(s.name);

    // You can also use dots with struct pointers - the
    // pointers are automatically dereferenced.
    sp := &s;
    fmt.Println(sp.age);

    // Structs are mutable.
    sp.age = 51;
    fmt.Println(sp.age);
};
