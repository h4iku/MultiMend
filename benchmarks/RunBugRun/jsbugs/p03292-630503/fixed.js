const main = (arg) => {
  const lines = arg.trim().split('\n');
  const A = lines[0].split(' ').map((x) => Number.parseInt(x));
  A.sort((a, b) => b - a);
  console.log(A[0] - A[2]);
};
main(require('fs').readFileSync('/dev/stdin', 'utf8'));
