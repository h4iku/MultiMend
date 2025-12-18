let [a, b] = require("fs")
                 .readFileSync("/dev/stdin", "utf8")
                 .split(" ")
                 .map(n => n.trim());
console.log(a == b ? "H" : "D");