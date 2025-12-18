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
  var lSort = l.sort(function(a, b) {
    if (a < b)
      return 1;
    if (a > b)
      -1;
    return 0;
  });

  //前からk個足す
  var ans = 0;
  for (var i = 0; i < k; i++) {
    ans += parseInt(lSort[i]);
  }

  console.log(ans);
});
