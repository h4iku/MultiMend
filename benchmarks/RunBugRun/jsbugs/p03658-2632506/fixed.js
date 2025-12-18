process.stdin.resume();
process.stdin.setEncoding('utf8');
// Here your code !
process.stdin.on('data', function(chunk) {
  var lines = chunk.toString().split("\n");
  var nk = lines[0].toString().split(" ");
  var n = parseInt(nk[0], 10);
  var k = parseInt(nk[1], 10);
  var l = lines[1].toString().split(" ");

  // Lを大きい数順に並べる。
  var lSort = l.sort(function(a, b) { return b - a; });

  //前からk個足す
  var ans = 0;
  for (var i = 0; i < k; i++) {
    ans += parseInt(lSort[i], 10);
  }
  console.log(ans);
});
