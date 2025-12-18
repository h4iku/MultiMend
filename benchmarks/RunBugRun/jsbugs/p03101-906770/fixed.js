var lines = [];
var reader = require('readline').createInterface({
  input : process.stdin,
  output : process.stdout
});
reader.on('line', (line) => { lines.push(line); });
reader.on('close', () => {
  var a = lines[0].split(" ");
  var b = lines[1].split(" ");
  console.log((a[0] - b[0]) * (a[1] - b[1]));
});