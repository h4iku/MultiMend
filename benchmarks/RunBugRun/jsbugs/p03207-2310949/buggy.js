function main(input) {
  var args = input.split("\n");
  var count = 1;
  var len = args[0];
  var exp = 0;
  var exp_p = 0;

  while (count <= len) {
    if (exp < parseInt(args[count])) {
      exp = parseInt(args[count]);
      exp_p = count;
    }
    count++;
  }

  var total = 0;

  count = 1;
  while (count <= len) {
    if (count != exp_p) {
      total += parseInt(args[count]);
    }
    count++;
  }
  console.log(total + " bf");
  total += exp / 2;
  console.log("" + total);
}

main(require('fs').readFileSync('/dev/stdin', 'utf8'));