"use strict";

function main(input) {
  input = input.trim().split("");

  for (let i = 0; i < input.length; i++) {
    if (input[i] == "?") {
      input[i] = "D";
      // if (input[i + 1] == "D" || input[i + 1] == "?") {
      //   input[i] = "P";
      // }
    }
  }

  console.log(input.join(""));
}

main(require("fs").readFileSync("/dev/stdin", "utf-8"));
