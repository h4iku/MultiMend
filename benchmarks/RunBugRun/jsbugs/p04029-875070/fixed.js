function main(input) {
  input = input.trim();
  const [a] = input.split(" ").map(Number);
  console.log(a * (a + 1) / 2);
}
main(require('fs').readFileSync('/dev/stdin', 'utf8'));