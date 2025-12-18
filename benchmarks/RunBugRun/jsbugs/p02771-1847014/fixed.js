'use strict';
const main =
    (input) => {
      const inputData = input.split(' ');
      const a = parseInt(inputData[0], 10);
      const b = parseInt(inputData[1], 10);
      const c = parseInt(inputData[2], 10);
      if ((a == b || b == c || c == a) && (a !== b || b !== c || c !== a)) {
        console.log('Yes');
      } else {
        console.log('No');
      }
    }

main(require("fs").readFileSync("/dev/stdin", "utf8"));