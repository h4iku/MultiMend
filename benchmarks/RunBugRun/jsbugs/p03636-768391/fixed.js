'use strict'

function main(s) {
  let n = s.split("\n")[0].split('');
  let init = n.slice(0)[0];
  let end = n.slice(-1)[0];
  let num = n.length - 2;
  console.log(`${init}${num}${end}`);
}

main(require("fs").readFileSync("/dev/stdin", "utf8"));