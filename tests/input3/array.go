package main;

// global array
var studentList [101]string;

func main() {
	var tutors [6]string;
	for i := 0; i < 101; i++ {
		studentList[i] = tutors[i%6];
	};
};