"use strict";
function Main(input) {
  let xs = input.trim().split(' ')
  // console.log(xs[0],xs[1]);
  if (xs[0] == 'D' && xs[1] == 'D') {
    consoule.log('H');
  }
  else if (xs[0] == 'H' && xs[1] == 'H') {
    console.log('H');
  }
  else {
    console.log('D');
  }
}
Main(require('fs').readFileSync('/dev/stdin', 'utf8'));