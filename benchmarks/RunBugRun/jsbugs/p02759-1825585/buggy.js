function main(input) {
  var N = parseInt(input[0], 10);

  if ((N % 2) === 0) {
    console.log(N / 2);
  } else {
    console.log((N + 1) / 2);
  }
}
main(require('fs').readFileSync('/dev/stdin', 'utf8'));