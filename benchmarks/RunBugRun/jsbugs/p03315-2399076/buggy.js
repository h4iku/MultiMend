function Main(input) {
  const inputs = input.split(/\s/g)[0].split('');
  const patterns = inputs.map((sign) => sign === '+' ? 1 : -1);
  console.log(inputs);
  const result = patterns.reduce((prev, current) => prev + current, 0);
  console.log('%s', result);
}

Main(require("fs").readFileSync("/dev/stdin", "utf8"));
