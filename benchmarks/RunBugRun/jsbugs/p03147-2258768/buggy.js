"use strict";

function totalH(H) { return H.reduce((a, b) => a + b) }

function main(arg) {
  const input = arg.trim().split("\n");
  const N = Number(input.shift())
  const H = input[0].split(" ").map(h => Number(h))

  // console.log(N)
  // console.log(H)

  let counter = 0
  while (totalH(H) > 0) {
    // find where is the largest part in current layer
    let len = 0, maxLen = 0, lastH = N - 1
    for (let i = 0; i < N; i++) {
      if (H[i] > 0) {
        len++
        // console.log(`len countup ->${len}`)
      } else {
        // console.log(`len=${len}`)
        if (maxLen < len) {
          // console.log(`i=${i}, len=${len}`)
          maxLen = len - 1
          lastH = i - 1
        }
        len = 0
      }
    }
    if (len == N)
      maxLen = N - 1
      let l = lastH - maxLen, r = lastH
      // console.log(`maxLen=${maxLen}, lastH=${lastH}, l=${l}, r=${r}`)
      for (let i = l; i <= r; i++) {
        if (H[i] > 0) {
          H[i]--
        }
      }
    // console.log(H)
    counter++
  }
  console.log(counter)
}

main(require("fs").readFileSync("/dev/stdin", "utf8"));