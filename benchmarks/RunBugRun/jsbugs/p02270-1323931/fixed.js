(function main() {
  let lines =
      require('fs').readFileSync('/dev/stdin', 'utf8').trim().split("\n");
  let [n, k] = lines.shift().split(' ').map(Number);
  let w = lines.map(Number);

  const canAllStack = (p) => {
    let cnt = 0;
    for (let i = 0; i < k; i++) {
      let sum = 0;
      for (; sum + w[cnt] <= p;) {
        sum += w[cnt++];
        if (cnt === n)
          return true;
      }
    }
    return false;
  };

  let p = Math.floor(w.reduce((a, b) => a + b) / k) - 1;
  while (!canAllStack(++p))
    ;
  console.log(p);
})();
