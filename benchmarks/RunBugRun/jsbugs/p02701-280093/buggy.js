function main(input) {
  const i = input.split('\n');
  const n = parseInt(i[0]);
  const map = new Map();
  for (let k = 1; k < n; k++) {
    if (!map.get(i[k]))
      map.set(i[k], 1);
    else
      map.set(i[k], map.get(i[k]) + 1);
  }
  console.log(map.size);
}
main(require('fs').readFileSync('/dev/stdin', 'utf8'));