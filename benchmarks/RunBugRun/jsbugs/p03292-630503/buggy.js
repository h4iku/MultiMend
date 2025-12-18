const main = (arg) => {
  const lines = arg.trim().split('\n');
  const A = lines[0].split(' ').map((x) => Number.parseInt(x));
  A.sort((a, b) => b - a);
  console.log(A[2] - A[0]);
};
main(require('fs').readFileSync('/dev/stdin', 'utf8'));
