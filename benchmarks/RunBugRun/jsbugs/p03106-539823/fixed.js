function Main(input) {
  i = input.split(" ").map(Number);
  r = [];
  for (a = 1; a <= Math.min(i[0], i[1]); a++) {
    if (i[0] % a === 0 && i[1] % a === 0) {
      r.push(a);
    }
  }
  console.log(r[r.length - i[2]]);
}
Main(require("fs").readFileSync("/dev/stdin", "utf8"));