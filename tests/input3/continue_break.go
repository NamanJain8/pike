package main;

func main() {
	attendence := 100;
	var dropCourse bool;
	dropCourse = false;
	for i := 0; i < 100;i++ {
		if attendence < 75 {
			dropCourse = true;
			break;
		};
		friday := i%3;
		if friday != 0 {
			continue;
		};
		attendence--;
	};
	repeat := dropCourse;
};