'use strict'

function main(input) {

  input = input.split('');
  var plus = 0;
  var minus = 0;
  for (var i = 0; i < input.length; i++) {
    if (input[i] == '+')
      plus++;
    else
      minus--;
  }

  console.log(plus - minus)
}

main(require("fs").readFileSync("/dev/stdin", "utf8"));
