function main(input) {
  const lines = input.split('\n');
  const N = lines.split(' ').map(x => parseInt(x))[0];
  const K = lines.split(' ').map(x => parseInt(x))[1];

  console.log(N - K + 1)
}

main(require('fs').readFileSync('/dev/stdin', 'utf8'));