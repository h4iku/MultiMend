function main(input) {
  input = input.trim();
  const a = parseInt(input.split(" ")[0], 10);
  const b = parseInt(input.split(" ")[1], 10);
  const c = parseInt(input.split(" ")[2], 10);
  const d = parseInt(input.split(" ")[3], 10);
  console.log(Math.min.apply(null, [ a, b ]) + Math.min.apply(null, [ c, d ]));
}
main(require('fs').readFileSync('/dev/stdin', 'utf8'));
