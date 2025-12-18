function main(arg) {
  arg = arg.trim().split("\n")
  var N = arg.shift()
  arg = arg.map(e => Number(e))
  var sum = 0
  var max = 0
  for (var i = 0; i < arg.length; i++) {
    if (arg[i] > max) {
      max = arg[i]
    }
    sum += arg[i]
  }
  console.log(parseInt(sum - (max / 2), 10))
}
main(require('fs').readFileSync('/dev/stdin', 'utf8'));
