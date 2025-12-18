function main(input) {

  var inputArr = input.split('');
  var sum = 0;
  for (var i = 0; i < input.length; i++) {
    if (inputArr[i] == '+') {
      sum++;
    } else {
      sum--;
    }
  }
  console.log(sum);
}
main(require('fs').readFileSync('/dev/stdin', 'utf8'));