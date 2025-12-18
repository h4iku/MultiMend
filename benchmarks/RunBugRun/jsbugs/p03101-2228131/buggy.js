'use strict'

function main(input) {
  const args = input.split('\n');
  const A = parseInt(args[0].split(' '));
  const gyou = A[0];
  const retu = A[1];

  const B = parseInt(args[1].split(' '));
  const selectG = B[0];
  const selectR = B[1];

  const all = gyou * retu;
  const kuro = selectG * retu + selectR * gyou - selectG * selectR;

  console.log(all - kuro);
}

main(require('fs').readFileSync('/dev/stdin', 'utf8'));