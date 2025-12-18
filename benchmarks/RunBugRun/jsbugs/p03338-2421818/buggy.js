'use strict'

function main(input) {
  input = input.split('\n')
  let ary = input[1].split('')
  let half = Math.ceil(input[0] / 2); // half
  let a, b = [];
  let cnt = 0
  let max = 0 // answer
  let matched = {};

  for (let i = half; i >= 0; i--) {
    //配列を真ん中で分断

    a = ary.slice(0, i)
    b = ary.slice(i, ary.length)

    // console.log(tmp[0], tmp[1])
    if (i >= max) { // max が 配列数より大きかったら停止

      cnt = 0
      matched = {}

      for (let j = 0; j < i; j++) {
        b.find(element => {
          if (element == a[j]) {
            matched[a[j]] = 1
          }
        })
      }
      cnt = Object.keys(matched).length

      max = (max > cnt) ? max : cnt
    }

    // i--
  }
  console.log(max)
}

main(require("fs").readFileSync("/dev/stdin", "utf8"));