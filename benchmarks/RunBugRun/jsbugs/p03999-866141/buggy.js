'use strict';

const lines = require("fs").readFileSync("/dev/stdin", "utf8").split("");
const ary = lines.map(str => Number(str));
const length = ary.length;

let sum = 0;
for (let i = 0; i < length; i++) {
  sum += calculator(i);
}
console.log(sum);

function calculator(i) {
  let total = 0;
  if (i === length - 1) {
    total += ary[length - 1] * Math.pow(2, length - 1);
  } else {
    for (let j = 0; j < length - i - 1; j++) {
      total += ary[i] * Math.pow(2, length - 2 - j) * Math.pow(10, j);
    }
    total += ary[i] * Math.pow(2, i) * Math.pow(10, length - i - 1);
  }
  return total;
};