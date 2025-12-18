function main(input) {
  input = input.trim();
  const inp = input.split("\n");
  const a = inp[0].split("");
  const b = inp[1].split("");
  var ans = 0;
  for (i = 0; i < 3; i++) {
    if (a[i] == b[i]) {
      ans++;
    }
  }
  console.log(ans);
}
main(require('fs').readFileSync('/dev/stdin', 'utf8'));