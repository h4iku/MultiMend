function Main(input) {
  var num = parseInt(input.split("\n")[0]);
  var sideLength = input.split("\n")[1].split(" ");

  for (var a = 0; a < num; a++) {
    sideLength[a] = parseInt(sideLength[a]);
  }

  sideLength.sort(function(a, b) {
    if (a > b) {
      return 1;
    } else if (a < b) {
      return -1;
    } else {
      return 0;
    }
  })

  var count = 0;

  if (num < 3) {
    console.log(0);
  } else {
    for (var i = 0; i < num; i++) {
      for (var j = i + 1; j < num; j++) {
        for (var k = j + 1; k < num; k++) {
          if (sideLength[i] != sideLength[j] &&
              sideLength[j] != sideLength[k] &&
              sideLength[i] != sideLength[k]) {
            if (sideLength[i] + sideLength[j] > sideLength[k]) {
              count = count + 1;
            }
          }
        }
      }
    }
  }
  if (count !== 0) {
    console.log(count);
  }
}
Main(require("fs").readFileSync("/dev/stdin", "utf8"));