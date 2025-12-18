function Main(input) {
  var tmp = input.trim().split('\n');
  var a = tmp[0].split(' ');
  var b = tmp[1].split(' ');
  var res = b.filter(function(val) { return val >= a[1]; })
  console.log(res.length);
}

/* var input = `1 500
499`;
Main(input);
 */
Main(require("fs").readFileSync("/dev/stdin", "utf8"));