'use strict'

function main(input) {
  const args = input.split('\n');
  const A = args[0].split(' ');
  const gyou = parseInt(A[0], 10);
  const retu = parseInt(A[1], 10);

  const B = args[1].split(' ');
  const selectG = parseInt(B[0], 10);
  const selectR = parseInt(B[1], 10);

  const all = gyou * retu;
  const kuro = selectG * retu + selectR * gyou - selectG * selectR;

  console.log(all - kuro);
}

main(require('fs').readFileSync('/dev/stdin', 'utf8'));