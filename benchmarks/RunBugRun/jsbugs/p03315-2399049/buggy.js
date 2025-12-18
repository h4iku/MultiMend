'use strict';

function Main(INPUT) {
  const S = INPUT.split("");
  let n = 0;
  for (let i = 0; i < S.length; i++) {
    n += S[i] == "+" ? 1 : 0;
  }
  console.log(n);
}

Main(require("fs").readFileSync("/dev/stdin", "utf8"));
