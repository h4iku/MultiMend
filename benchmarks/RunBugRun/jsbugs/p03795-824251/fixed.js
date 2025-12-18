function main(input) {
  input = input.trim();
  const N = parseInt(input.split(" ")[0], 10);
  console.log(800 * N - Math.floor((N / 15)) * 200);
}

main(require('fs').readFileSync('/dev/stdin', 'utf8'));