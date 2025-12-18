const main = (arg) => {
  const lines = arg.trim().split('\n');
  const S = lines[0].split('');
  let ans = 0;
  S.forEach((c) => { ans += c === '+' ? 1 : -1; });
  console.log(ans);
};
main(require('fs').readFileSync('/dev/stdin', 'utf8'));
