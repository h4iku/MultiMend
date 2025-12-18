function main(input) {
  input = input.trim();
  const n = parseInt(input.split(" ")[0], 10);
  const m = parseInt(input.split(" ")[1], 10);
  const x = parseInt(input.split(" ")[2], 10);
  const arrA = input.split('\n')[1].split(' ').map((n) => parseInt(n, 10));

  var temp1 = 0
  var temp2 = 0
  for (var i = 0; i < m; i++) {
    if (arrA[i] < x) {
      temp1++
    } else {
      temp2++
    }
  }
  console.log(Math.min.apply(null, [ temp1, temp2 ]));
}

main(require('fs').readFileSync('/dev/stdin', 'utf8'));
