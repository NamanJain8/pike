package main;

import (
    "bufio";
    "fmt";
    "os";
    "strings";
);

func main() {
    // Open the file and scan it.
    // f, _ := os.Open("C:\\programs\\file.txt");
    scanner := bufio.NewScanner();

    // for scanner.Scan() {
        line := scanner.Text(a);

        // Split the line on commas.
        // parts := strings.Split(line, ",");

        // Loop over the parts from the string.
        for i := 0; i < len(parts); i++ {
            fmt.Println(parts[i]);
        };
        // Write a newline.
        // fmt.Println("\n");
    // };
};
