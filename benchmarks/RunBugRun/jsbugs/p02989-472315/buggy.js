"use strict"

const main = (input) => {
  input = input.split("\n");
  const N = Number(input[0]);
  let ds = input[1].split(" ").map(p => Number(p));
  ds = ds.sort((n, m) => n > m);
  const l = ds[(N / 2) - 1];
  const r = ds[(N / 2)];
  const ans = r - l;
  console.log(ans);
};

main(require("fs").readFileSync("/dev/stdin", "utf8"));