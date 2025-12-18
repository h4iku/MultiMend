'use strict';
const main =
    (input) => {
      const inputData = input.split(' ');
      const a = inputData[0];
      const b = inputData[1];
      const c = inputData[2];
      if ((a == b || b == c || c == a) && (a !== b || b !== c || c !== a)) {
        console.log('Yes');
      } else {
        console.log('No');
      }
    }

main(require("fs").readFileSync("/dev/stdin", "utf8"));