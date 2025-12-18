var lines = [];
var reader = require('readline').createInterface({
  input : process.stdin,
  output : process.stdout
});
reader.on('line', (line) => { lines.push(line); });
reader.on('close', () => {
  let a = lines[0].split(" ");
  let b = lines[1].split(" ");
  Console.log((a[0] - b[0]) * (a[1] - b[1]));
});