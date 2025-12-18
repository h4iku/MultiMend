var input = require('fs').readFileSync('/dev/stdin', 'utf8');
var Arr = (input.trim()).split("\n");
var x = Arr[0] - 0;
for (var i = 1; i < arr.length - 1; i = i + 2) {
  if (arr[i] == "+")
    x += arr[i + 1] - 0;
  if (arr[i] == "-")
    x -= arr[i + 1] - 0;
  if (arr[i] == "*")
    x *= arr[i + 1] - 0;
  if (arr[i] == "/")
    x /= arr[i + 1] - 0;
  x = x.toFixed(0);
}
console.log(x);