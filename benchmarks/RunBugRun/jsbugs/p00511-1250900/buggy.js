var input = require('fs').readFileSync('/dev/stdin', 'utf8');
var arr = (input.trim()).split("\n");
var x = arr[0] - 0;
for (var i = 1; i < arr.length; i = i + 2) {
  if (arr[i] == "=")
    break;
  if (arr[i] == "+")
    x += (arr[i + 1] - 0);
  if (arr[i] == "-")
    x -= (arr[i + 1] - 0);
  if (arr[i] == "*")
    x *= (arr[i + 1] - 0);
  if (arr[i] == "/")
    x /= (arr[i + 1] - 0);
  x = x.toFixed(0) - 0;
}
console.log(x);
});