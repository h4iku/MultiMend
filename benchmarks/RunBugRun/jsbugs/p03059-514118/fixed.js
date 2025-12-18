function main(input) {
  var args = input.split(' ');
  var a = parseInt(args[0]);
  var b = parseInt(args[1]);
  var t = parseInt(args[2]);
  var biscuit = Math.floor(t / a) * b;
  console.log(biscuit);
}
main(require('fs').readFileSync('/dev/stdin', 'utf8'));