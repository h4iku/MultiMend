function Main(input) {
  input = input.split("\n");
  const n = parseInt(input[0], 10);
  const l = input[1].split(" ").map(v => parseInt(v, 10));

  let count = 0;
  for (let i = 0; i < n; i++) {
    for (let j = i + 1; j < n; j++) {
      for (let k = j + 1; k < n; k++) {
        if (!allUnique(l[i], l[j], l[k])) {
          continue;
        }
        if (isTriangle(l[i], l[j], l[k])) {
          count++;
        }
      }
    }
  }

  console.log(count);
}

function allUnique(a, b, c) {
  if (a !== b && a !== c && b !== c) {
    return true;
  }
  return false;
}

function isTriangle(a, b, c) {
  if (a + b > c && b + c > a && c + a > b) {
    return true;
  }
  return false;
}

Main(require("fs").readFileSync("/dev/stdin", "utf8"));