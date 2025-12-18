let [a, b] = require("fs").readFileSync("/dev/stdin", "utf8").split(" ").trim();
console.log(a == b ? "H" : "D");