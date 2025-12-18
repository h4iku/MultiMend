'use strict'
function main(input) {
  const tmp = Array.from(input.split('\n'));
  const N = parseInt(tmp[0], 10);
  const A = tmp[1].split(' ').map((elem) => parseInt(elem, 10));

  let X = [];
  const S = A.reduce((sum, elem) => sum + elem);
  const A2 =
      A.filter((elem, i) => i % 2 !== 0).reduce((sum, elem) => sum + elem);
  X[0] = S - 2 * A2;

  for (let i = 1; i < N; i++) {
    X[i] = 2 * A[i - 1] - X[i - 1];
  }

  console.log(X);
}

main(require('fs').readFileSync('/dev/stdin', 'utf8'));