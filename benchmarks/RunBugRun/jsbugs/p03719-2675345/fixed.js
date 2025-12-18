process.stdin.resume();
process.stdin.setEncoding('utf8');
// Here your code !

process.stdin.on('data', function(chunk) {
  var lines = chunk.toString().split(' ');
  var A = parseInt(lines[0]);
  var B = parseInt(lines[1]);
  var C = parseInt(lines[2]);

  if (C >= A && C <= B) {
    console.log("Yes");
  } else {
    console.log("No");
  }
});
