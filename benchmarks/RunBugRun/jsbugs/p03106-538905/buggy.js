function main(input) {
  const args = input.split(' ');
  var A = parseInt(args[0], 10);
  var B = parseInt(args[1], 10);
  var K = parseInt(args[2], 10);

  var max = A;
  if (A < B) {
    max = B;
  }

  var ans = [];
  var ans_cout = 0;

  for (var i = 1; i < max; i++) {
    if (A % i === 0 && B % i === 0) {
      ans.push(i);
    }
  }

  console.log(ans[ans.length - K])
}
main(require('fs').readFileSync('/dev/stdin', 'utf8'));
