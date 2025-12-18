function Main(input) {
  input = input.split("\n");
  var n = parseInt(input[0], 10);
  s = input[1];
  var char = new Array(26);
  var l = new Array(26);
  var r = new Array(26);
  for (var i = 0; i < 26; i++) {

    for (l[i] = 0; l[i] < 26; l[i]++) {
      if (s.charCodeAt(l[i]) == i + 97) {
        break;
      }
    }

    if (l[i] < 25) {
      for (r[i] = 25; r[i] >= l[i]; r[i] += -1) {
        if (s.charCodeAt(r[i]) == i + 97) {
          break;
        }
      }
    }
  }
  var counter;
  var max = 0;
  for (var j = 0; j < n; j++) {
    counter = 0;
    for (var k = 0; k < 26; k++) {
      if (j >= l[k] && j < r[k]) {
        counter++;
      }
    }
    if (counter > max) {
      max = counter;
    }
  }
  console.log('%d', max);
}
Main(require("fs").readFileSync("/dev/stdin", "utf8"));