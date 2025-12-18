function main(input) {
  input = input.trim();
  const [a, b, c] = input.split(" ").map(Number);

  if (a >= c && b <= c) {
    console.log("Yes");
  } else {
    console.log("No");
  }
}
main(require("fs").readFileSync("/dev/stdin", "utf8"));