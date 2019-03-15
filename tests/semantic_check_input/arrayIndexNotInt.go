package main;

func main() {
	var coolMovies [250]string; // IMDB top 250
	top := "first"; // this should have been top := 0
	firstMovie := coolMovies[top]; // [Error]

	var grades [-100]string; // [Error]
};
