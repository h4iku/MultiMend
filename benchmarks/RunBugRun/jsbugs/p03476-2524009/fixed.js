var lines = [];
var readline = require('readline');

var rl = readline.createInterface({
  input : process.stdin,
  output : process.stdout,
});

rl.on('line', function(x) { lines.push(x); });

rl.on('close', function() {
  var Q = Number(lines[0]);
  lines.shift();
  var lr = lines.map(i => i.split(" ").map(i => Number(i)));

  var x = lr.concat().sort((a, b) => b[1] - a[1])
  var max = x[0][1];

  var sum = Array(max + 1).fill(0);

  sum[0] = 0;
  sum[1] = 0;
  sum[2] = 0;
  sum[3] = 1;
  sum[4] = 1;

  // 累積和
  for (var i = 5; i <= max; i++) {
    for (var j = 2; j <= Math.sqrt(i); j++) {
      // 素数でなければ，break
      if (i % j === 0) {
        break;
      }

      // (i + 1) / 2が整数でない場合，素数でないのでbreak
      if ((i + 1) / 2 !== Math.floor((i + 1) / 2)) {
        break;
      }

      // (i + 1) / 2が素数でなければ，break
      if (((i + 1) / 2) % j === 0) {
        break;
      }

      // 素数なら，sum++
      if (j === Math.floor(Math.sqrt(i))) {
        sum[i]++;
      }
    }
    // 累積和
    sum[i] += sum[i - 1];
  }

  for (var i = 0; i < Q; i++) {
    console.log(sum[lr[i][1]] - sum[lr[i][0] - 1]);
  }
});