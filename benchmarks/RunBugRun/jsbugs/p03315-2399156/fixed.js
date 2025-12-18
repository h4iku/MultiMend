function main(input) {

  var inputArr = input.split('');
  var sum = 0;
  for (var i = 0; i < 4; i++) {
    if (inputArr[i] == '+') {
      sum += 1;
    } else {
      sum -= 1;
    }
  }
  console.log(sum);
}
main(require('fs').readFileSync('/dev/stdin', 'utf8'));