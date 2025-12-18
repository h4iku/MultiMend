const input = require("fs").readFileSync("/dev/stdin", "utf8").trim();
let b = [];
for (let bit = 0; bit < 1 << input.length - 1; bit++) {
  let a = [];
  for (let shift = 0; shift < input.length - 1; shift++) {
    if ((bit >> shift) & 1)
      a.push(1);
    else
      a.push(0);
  }
  b.push(a);
}
let sum = 0;
b.forEach((array) => {
  let tmpSum = 0;
  let str = "";
  console.log(array);
  Array.prototype.forEach.call(input, (item, index) => {
    str += item;
    if ((index === (input.length - 1) || array[index] === 1)) {
      tmpSum += Number(str);
      str = "";
    }
  })
  sum += tmpSum;
});
console.log(sum);