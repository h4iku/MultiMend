function main(input) {
  var a = parseInt(input.split("\n")[0].split(" ")[0]);
  var b = parseInt(input.split("\n")[0].split(" ")[1]);
  var c = parseInt(input.split("\n")[0].split(" ")[2]);
  var d = parseInt(input.split("\n")[0].split(" ")[3]);

  if (a * b >= c * d) {
    console.log(a * b);
  } else {
    console.log(c * d);
  }
}

main(require("fs").readFileSync("/dev/stdin", "utf8"));