'use strict';
function main(input) {
  input = input.split("\n");
  const input1 = input[0].split(" ");
  const heights = input[1].split(" ");
  const num = input1[0], threshold = input1[1];

  let count = 0;
  for (let i = 0; i < num; i++) {
    if (parseInt(heights[i]) < parseInt(threshold)) {
      continue;
    }
    count++;
  }

  return count;
}

var input = require("fs").readFileSync("/dev/stdin", "utf8");
console.log(main(input));