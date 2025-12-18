var lines = [];

var readline = require("readline");
var rl =
    readline.createInterface({input : process.stdin, output : process.stdout});

rl.on('line', function(x) { lines.push(x); });

rl.on('close', function() {
  var tmp = lines[0].split(" ");

  var a = Number(tmp[0]);
  var b = Number(tmp[1]);
  var k = Number(tmp[2]);
  var counter = 0;

  for (var i = 100; i >= 1; i--) {
    if (a % i === 0 && b % i === 0) {
      counter++;
    }
    if (counter === k) {
      console.log(i);
      break;
    }
  }
});