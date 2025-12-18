var readable = process.stdin;
readable.resume();
readable.setEncoding('utf-8');
readable.on('data', function(chunk) {
  input += chunk;
  var data = chunk.split(" ").map(Number);
  var a = data[0];
  var b = data[1];
  var C = data[2] * (Math.PI / 180);

  var h = Math.sin(C) * b;
  var ta = Math.cos(C) * b;
  var c = Math.sqrt(Math.pow((a - ta), 2) + Math.pow(h, 2));

  var S = (a * h) / 2;
  var L = a + b + c;
  console.log(S + '\n' + L + '\n' + h);
});