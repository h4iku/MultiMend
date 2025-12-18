'use strict'
function Main(input) {
  let Nums = input.split('\n');
  let Info = Nums[0].split(' ');
  let Border = Info[1];
  let Row = Nums[1].split(' ').sort((a, b) => {return a - b});
  let FilterRow = Row.filter((x) => {return x >= Border});
  console.log(FilterRow.length);
}

Main(require("fs").readFileSync("/dev/stdin", "utf8"));
