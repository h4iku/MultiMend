function Main(input) {
  readAsNumArray(input);
  var N = input.shift();
  var reversedBinary = [];
  for (let i = 0; i < N; i++) {
    reversedBinary[i] =
        parseInt(input[i]).toString(2).split('').reverse().join('');
  }
  var counter = 0;
  for (let i = 0; i < N; i++) {
    while (reversedBinary[0] === '0') {
      reversedBinary.replace('0', '');
      counter++;
    }
  }
  console.log(counter);
}

function readAsNumArray(input) {

  var I = [], i = 0;

  var checkNum = /^\d+/;

  var checkSpace = / +|\n+/;

  while (input.length > 0) {

    if (input.match(checkNum) !== null) {

      I[i] = input.match(checkNum)[0];

      input = input.replace(checkNum, "");

      i++;

      continue;
    }

    input = input.replace(checkSpace, "");

    continue;
  }

  return input = I;
}

Main(require('fs').readFileSync('/dev/stdin', 'utf8'))