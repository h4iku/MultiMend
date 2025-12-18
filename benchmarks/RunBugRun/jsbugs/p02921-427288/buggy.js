function Main(input) {
  input = input.split("\n");
  const result = Array.from(input[0])
                     .forEach((item, index) => item === input[1][index])
                     .length;
  console.log(result)
}
Main(require("fs").readFileSync("/dev/stdin", "utf8"));