"use strict"

function Main(input) {
  var ex = input[0].split('');
  var result = input[1].split('');

  var sum = 0;
  for (i = 0; i < 3; i++) {
    if (ex[i] === result[i]) {
      sum++;
    }
  }
  console.log(sum);
}

Main(require("fs").readFileSync("/dev/stdin", "utf8").trim().split(/\n|\s/));