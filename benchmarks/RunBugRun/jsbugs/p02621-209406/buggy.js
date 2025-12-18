function main(input) {
  var a = Number(input[0]);

  console.log(a + a ** 2 + a ** 3);
}

main(require("fs").readFileSync("/dev/stdin", "utf8"));