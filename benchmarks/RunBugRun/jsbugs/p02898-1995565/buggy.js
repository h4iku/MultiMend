'use strict'

const main =
    (INPUT) => {
      const input = INPUT.split('\n')
      const [N, K] = input[0].split(' ')
      const h = input[1].split(' ')
      let ans = 0
      for (let i = 0; i < h.length; i++) {
        if (h[i] >= K) {
          ans++
        }
      }
      console.log(ans)
    }

main(require('fs').readFileSync('/dev/stdin', 'utf8'))
