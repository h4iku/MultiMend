function Main(input) {
  input = input.trim();
  var len = parseInt(input.split("\n")[0]);
  var A = input.split("\n")[1];
  var B = input.split("\n")[2];
  var C = input.split("\n")[3];
  var count = 0;
  if (A == B && B == C) {
    console.log(count);
    return;
  }
  for (var i = 0; i < len; i++) {
    var tmpA = A.slice(i, i + 1);
    var tmpB = B.slice(i, i + 1);
    var tmpC = C.slice(i, i + 1);
    if (tmpA == tmpB && tmpB == tmpC) {
      continue;
    } else if (tmpA != tmpB && tmpB != tmpC) {
      count += 2;
    } else {
      count++;
    }
  }
  console.log(count);
}

Main(require("fs").readFileSync("/dev/stdin", "utf8"));
