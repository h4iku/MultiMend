function main(arg) {
  arg = arg.trim().split('\n');
  arg = arg.map(str => parseInt(str, 10));
  var a = arg[0], b = arg[1];
  var num = [ 1, 2, 3 ];
  var out = num.filter(o => o !== a && o != b);
  console.log(out[0]);
}
main(require('fs').readFileSync('/dev/stdin', 'utf8'));