function Main(input) {
  input = input.trim().split(/\s+/).map(x => x - 0);
  var N = input.shift();
  var M = input.shift();
  var X = input.shift();
  var d = 0, u = M - 1;
  var m = Math.floor((d + u) / 2);
  while (d <= u) {
    if (X < input[m])
      u = m - 1;
    else
      d = m + 1;
    m = Math.floor((d + u) / 2);
  }
  console.log(Math.min(m + 1, M - m - 1));
}

Main(require('fs').readFileSync('/dev/stdin', 'utf8'));
