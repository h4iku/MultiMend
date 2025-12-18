function main(input) {
  var N = parseInt(input[0]);
  console.log(800 * N - 150 * Math.floor(N / 15));
}

main(require("fs").readFileSync("/dev/stdin", "utf8").split("\n"));
