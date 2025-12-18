"use strict";
var input = require("fs").readFileSync("/dev/stdin", "utf8");
var cin = input.split(/ |\n/), cid = 0;

function next() { return +cin[cid++]; }           // number一個取得
function nextstr() { return cin[cid++]; }         // 文字列一個取得
function nextbig() { return BigInt(cin[cid++]); } // BigInteger一個取得
// 長さnの配列として取得。aは文字列フラグ
function nexts(n, a) {
  return a ? cin.slice(cid, cid += n) : cin.slice(cid, cid += n).map(a => +a);
}
// 長さnのBigInt配列として取得。
function nextsbig(n) { return cin.slice(cid, cid += n).map(a => BigInt(a)); }
// w個ずつを組にして長さhの配列。aは文字列フラグ。
function nextm(h, w, a) {
  var r = [], i = 0;
  if (a)
    for (; i < h; i++)
      r.push(cin.slice(cid, cid += w));
  else
    for (; i < h; i++)
      r.push(cin.slice(cid, cid += w).map(a => +a));
  return r;
}
// 多次元配列。v,a1,a2,a3
// なら、3次元。[[値vで長さa3の配列]をa2個並べた配列]をa1個並べた配列。
function xArray(v) {
  var a = arguments, l = a.length,
      r = "Array(a[" + --l + "]).fill().map(x=>{return " + v + ";})";
  while (--l)
    r = "Array(a[" + l + "]).fill().map(x=>" + r + ")";
  return eval(r);
}

console.log(main());

function main() {
  let N = next();
  let K = next();
  let A = nexts(N);
  let t = xArray(0, N + 1);
  let B = Array(N);
  let i, j, k, left, right;
  for (k = 0; k < K; k++) {
    let left = xArray(0, N + 1);
    let right = xArray(0, N + 1);
    for (i = 0; i < N; i++) {
      // 各Aiの電球が各点zahyoを照らしているかどうかをチェックする。
      left[Math.max(i + 1 - A[i], 1) - 1]++;
      right[Math.min(i + 1 + A[i], N) - 1]++;
    }
    // console.log({left,right});
    // 両端にすべての灯りが届いているかどうかをチェック。
    if (left[0] == N && right[N - 1] == N) {
      return xArray(n, n).join(" ");
    }
    A[0] = left[0];
    for (i = 1; i < N; i++) {
      A[i] = A[i - 1] + left[i] - right[i - 1];
    }
  }
  return A.join(" ");
}