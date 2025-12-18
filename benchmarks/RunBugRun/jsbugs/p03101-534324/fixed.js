function Main(input) {
  const inputs = input.split('\n');
  const whiteH = Number(inputs[0].split(' ')[0]);
  const whiteW = Number(inputs[0].split(' ')[1]);
  const blackH = Number(inputs[1].split(' ')[0]);
  const blackW = Number(inputs[1].split(' ')[1]);

  console.log(whiteH * whiteW - (blackH * whiteW + blackW * whiteH) +
              (blackW * blackH));
};

Main(require("fs").readFileSync("/dev/stdin", "utf8"));