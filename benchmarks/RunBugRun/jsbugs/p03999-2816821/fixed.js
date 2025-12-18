"use strict";
const input = require("fs").readFileSync("/dev/stdin", "utf8").trim();

const n = input.length - 1;

if (n === 0) {
  console.log(Number(input))
} else {
  let sum = 0;
  for (let i = 0; i < 1 << n; i++) {
    let str = "";
    for (let shift = 0; shift < n; shift++) {
      str = input[n - shift] + str;
      if ((i >> shift) & 1) {
        sum += Number(str);
        str = "";
      }

      if (shift === n - 1) {
        str = input[0] + str;
        sum += Number(str);
        str = "";
      }
    }
  }
  console.log(sum);
}