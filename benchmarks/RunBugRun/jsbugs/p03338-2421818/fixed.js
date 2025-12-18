'use strict'

function main(input) {

  input = input.split('\n')
  let ary = input[1].split('')
  let a, b = [];
  let cnt = 0
  let max = 0 // answer
  let matched = {};

  for (let i = 0; i < ary.length; i++) {

    a = ary.slice(0, i)
    b = ary.slice(i, ary.length)

    if (i >= max) { // max が 配列数より大きかったら停止

      cnt = 0
      matched = {}

      for (let j = 0; j < i; j++) {
        b.find(element => {
          if (element == a[j]) {
            matched[a[j]] = true
          }
        })
      }
      cnt = Object.keys(matched).length

      max = (max > cnt) ? max : cnt
    }
  }
  console.log(max)
}

main(require("fs").readFileSync("/dev/stdin", "utf8"));