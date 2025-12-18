
function Main(input) {
  var r = parseInt(input[0], 10);
  var D = parseInt(input[1], 10);
  var x2000 = parseInt(input[1], 10);

  var xi = r * x2000 - D; // 2001がまず入る

  for (var i = 1; i <= 10; i++) {
    if (i === 1) {
      console.log(xi);
    } else {
      xi = r * xi - D;
      console.log(xi);
    }
  }
}

Main(require("fs").readFileSync("/dev/stdin", "utf8").trim().split(/\n|\s/));