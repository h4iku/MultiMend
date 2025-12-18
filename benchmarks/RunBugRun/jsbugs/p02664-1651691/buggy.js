"use strict";

function main(input) {
  input = input.trim().split("");
  console.log(`input: ${input}`);

  for (let i = 0; i < input.length; i++) {
    if (input[i] == "?") {
      input[i] = "D";
    }
  }

  console.log(input.join(""));
}

main(require("fs").readFileSync("/dev/stdin", "utf-8"));
