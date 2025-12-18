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
      // console.log("全て同じ(+0)");
      continue;
    } else if (tmpA != tmpB && tmpB != tmpC && tmpA != tmpC) {
      // console.log("全て違う(+2)");
      count += 2;
    } else {
      // console.log("その他(+1)");
      count++;
    }
  }
  console.log(count);
}

Main(require("fs").readFileSync("/dev/stdin", "utf8"));
