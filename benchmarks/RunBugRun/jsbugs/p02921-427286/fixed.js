function Main(input) {
  arr = input.split("\n");
  const S = arr[0];
  const T = arr[1];
  const result = Array.from(S).filter((s, i) => s === T[i]).length;
  console.log(result);
}
Main(require("fs").readFileSync("/dev/stdin", "utf8"));