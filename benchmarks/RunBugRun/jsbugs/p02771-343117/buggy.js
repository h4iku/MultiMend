const main =
    stdin => {
      const input = stdin.trim().split('\n')
      const [a, b, c] = input[0].split(' ').map(x => parseInt(x))
      if (a === b && b === c || a !== b && a !== c) {
        console.log('No')
      }
      else {
        console.log('Yes')
      }
    }

// 標準入力
main(require("fs").readFileSync("/dev/stdin", "utf8"))
