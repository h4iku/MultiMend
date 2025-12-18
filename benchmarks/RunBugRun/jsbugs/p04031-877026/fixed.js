'use strict'

const main =
    (INPUT) => {
      const input = INPUT.split('\n')[1].split(' ').map(n => Number(n))
      const sum = input.reduce((a, x) => a + x, 0)
      const ave = Math.round(sum / input.length)
      let ans = 0

      for (let i = 0; i < input.length; i++) {
        ans += Math.pow((input[i] - ave), 2)
      }
      console.log(ans)
    }

main(require('fs').readFileSync('/dev/stdin', 'utf8'))
