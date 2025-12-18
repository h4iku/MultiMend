const main =
    input => {
      const K = parseInt(input.trim())
      console.log(Math.floor((K / 2)) * Math.floor(((K + 1) / 2)))
    }
// 標準入力
main(require("fs").readFileSync("/dev/stdin", "utf8"));
