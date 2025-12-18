"use strict";
var input = require("fs").readFileSync("/dev/stdin", "utf8");
var cin = input.trim().split(/ |\n/), cid = 0;

let n = +cin.shift();
let B = {};
let C = {};
cin.forEach((v, i) => {
  const x = Number(v);
  B[i + x] = B[i + x] + 1 || 1;
  C[i - x] = C[i - x] + 1 || 1;
});
let ans = 0;
Object.keys(B).filter(i => C[i]).forEach(i => { ans += (B[i] * C[i]); });
console.log(ans);