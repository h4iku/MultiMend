function main(input) {
  const arrays = input.split(' ');
  const a = parseInt(arrays[0], 10) - 1;
  const b = parseInt(arrays[1], 10) - 1;
  console.log(a * b);
}
main(require('fs').readFileSync('/dev/stdin', 'utf8'));