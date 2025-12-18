'use strict'

function main(s) {

  const n = Number(s[0]);
  const circle = n * n;
  console.log(circle);
}

main(require("fs").readFileSync("/dev/stdin", "utf8"));
