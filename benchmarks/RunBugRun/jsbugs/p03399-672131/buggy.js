function Main(input) {
  input = input.split("\n");
  const a = Number(input[0]);
  const b = Number(input[1]);
  const c = Number(input[2]);
  const d = Number(input[3]);
  const result1 = Math.max(a, b)
  const result2 = Math.max(c, d)
  console.log(result1 + result2);
}
Main(require("fs").readFileSync("/dev/stdin", "utf8"));
