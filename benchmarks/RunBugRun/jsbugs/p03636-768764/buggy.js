function Main(input) {
  var first = input[0];
  var mid = input.length - 3;
  var last = input[input.length - 2];
  var result = first + mid + last;

  console.log(result);
}

Main(require("fs").readFileSync("/dev/stdin", "utf8"));
