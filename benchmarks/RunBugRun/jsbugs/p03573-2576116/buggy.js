function Main(input) {
  input = input.trim()
  input = input.split(" ").map(Number);
  if (input[0] != input[1] && input[0] = input[2]) {

    console.log(input[1])
  } else if (input[0] == input[1]) {

    console.log(input[2])
  } else {
    console.log(input[0])
  }
}
Main(require("fs").readFileSync("/dev/stdin", "utf8"));