function main(input) {
  input = input.trim();
  const n = parseInt(input.split(" ")[0], 10);
  var arrD = input.split('\n')[1].split(' ').map((n) => parseInt(n, 10));
  arrD.sort(function(a, b) {
    if (a < b)
      return -1;
    if (a > b)
      return 1;
    return 0;
  });
  console.log(arrD[(n / 2) + 1] - arrD[(n / 2)]);
}

main(require('fs').readFileSync('/dev/stdin', 'utf8'));
