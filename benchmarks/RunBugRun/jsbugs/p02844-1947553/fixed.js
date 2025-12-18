function Main(input) {
  input = input.trim().split("\n");
  var N = parseInt(input[0], 10);
  var S = input[1].split("");
  var now = [];
  var total = 0;

  for (var i = 0; i < 10; i++) {
    var is = String(i);
    if (S.indexOf(is) != -1) {
      now = S.slice(S.indexOf(is) + 1, N);
      if (now.length < 2)
        continue;
    } else {
      continue;
    }
    for (var j = 0; j < 10; j++) {
      var js = String(j);
      if (now.indexOf(js) != -1) {
        now2 = now.slice(now.indexOf(js) + 1, N);
        if (now.length < 1)
          continue;
      } else {
        continue;
      }
      for (var k = 0; k < 10; k++) {
        var ks = String(k);
        if (now2.indexOf(ks) != -1) {
          total++;
        } else {
          continue;
        }
      }
    }
  }

  console.log(total);
}

Main(require("fs").readFileSync("/dev/stdin", "utf8"));
