'use strict'
function Main(input) {
  let Nums = input.trim().split('\n');
  let Info = Nums[0].split(' ');
  let Border = Info[1];
  let Row = Nums[1].split(' ').sort((a, b) => {return a - b});
  let FilterRow = Row.filter((x) => {return x * 1 >= Border});
  console.log(FilterRow.length);
}

Main(require("fs").readFileSync("/dev/stdin", "utf8"));
