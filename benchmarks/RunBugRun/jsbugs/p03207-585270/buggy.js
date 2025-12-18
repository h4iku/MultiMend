function Main(input) {
  var inputArr = input.split("\n");
  var max = 0;
  var sum = 0;
  for (var i = 1; i < inputArr.length; i++) {
    var p = parseInt(inputArr[i], 10);
    ;
    if (p > max) {
      max = p;
    }
    sum = sum + p;
  }
  sum = sum - max / 2;
  console.log(sum);
}
Main(require("fs").readFileSync("/dev/stdin", "utf8"));