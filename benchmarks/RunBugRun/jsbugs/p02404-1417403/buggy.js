var reader = require('readline').createInterface({
  input : process.stdin,
  output : process.stdout
});
reader.on('line', function(line) {
  var i, j, result;
  var a = line.split(' ');
  var b = parseInt(a[0], 10);
  var c = parseInt(a[1], 10);
  if (!b && !c)
    process.exit();
  for (i = 0; i < b; i++) {
    result = "";
    for (j = 0; j < c; j++) {
      if (i == 0 || i == b - 1 || j == 0 || j == c - 1)
        result += "#";
      else
        result += ".";
    }
    console.log(result);
  }
});
process.stdin.on('end', function() {});