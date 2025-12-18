"use strict";

function Main(input) {
  input = input.split(" ");
  const a = parseInt(input[0], 10);
  const b = parseInt(input[1], 10);
  const k = parseInt(input[2], 10);

  let candidateCount = 0;
  let answer = 0;
  for (let i = 100; i > 0; i--) {
    if (a % i == 0 && b % i == 0) {
      candidateCount++;
    }

    if (candidateCount == k) {
      answer = i;
      break;
    }
  }

  console.log(answer);
}

Main(require("fs").readFileSync("/dev/stdin", "utf8"));
