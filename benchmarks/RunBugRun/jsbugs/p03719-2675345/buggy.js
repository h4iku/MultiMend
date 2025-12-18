process.stdin.resume();
process.stdin.setEncoding('utf8');
// Here your code !

process.stdin.on('data', function(chunk) {
  var lines = chunk.toString().split(' ');
  var A = lines[0];
  var B = lines[1];
  var C = lines[2];

  if (C >= A && C <= B) {
    console.log("Yes");
  } else {
    console.log("No");
  }
});
