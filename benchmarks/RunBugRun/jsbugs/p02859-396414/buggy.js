'use strict'
function Main(input) {
  input = input.split('');
  let r = input;
  let area = r * r;
  console.log(area);
}
Main(require("fs").readFileSync("/dev/stdin", "utf8"));
