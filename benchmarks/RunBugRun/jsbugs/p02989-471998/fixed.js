function main(input) {
  input = input.split("\n");
  const N = input[1].split(" ");
  let problems = [];
  let problemCount = 0

  for (problemCount = 0; problemCount < N.length; problemCount++) {
    problems[problemCount] = parseInt(N[problemCount], 10);
  }

  function compareFunc(a, b) { return a - b; }

  problems.sort(compareFunc);
  const ans = problems[N.length / 2] - problems[N.length / 2 - 1];

  console.log(ans);
}

main(require('fs').readFileSync('/dev/stdin', 'utf8'));