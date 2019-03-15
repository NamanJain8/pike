package main;

type person struct{
	age int;
	name string;
};

func main(){
	var p1,p3 type person;
	p1.name = p3.name;
	
	ageP1 := p1.age;
	ageP3 := p3.age;
	if ageP1 < ageP3 {
		msg := "hello old man, said person 1";
	};

};
