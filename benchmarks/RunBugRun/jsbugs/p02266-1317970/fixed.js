
let line = require('fs').readFileSync('/dev/stdin', 'utf8').trim().split('');
// 初めの上昇と平坦を除去
while (line.length > 0 && line[0] !== '\\')
  line.shift();
// 終わりの下降と平坦を除去
while (line.length > 0 && line[line.length - 1] !== '/')
  line.pop();

let height_list = [ 0 ];
let current_height = 0;
line.forEach(function(e, i) {
  if (e === '\\')
    current_height -= 1
    else if (e === '/') current_height += 1
    height_list.push(current_height);
});

let h, sum = 0;
let holes = [];
while (height_list.length > 1) {
  if (h = makeHole(height_list)) {
    sum += h;
    holes.push(h);
  }
}

console.log(sum);
console.log(holes.length && holes.length + ' ' + holes.join(' '));

function makeHole(list) {
  begin = list.shift();
  let area = 0;
  if (list[0] < begin &&
      begin <= list.reduce((a, b) => Math.max(a, b), -200000)) {
    while (!(list.length === 0 || begin <= list[0]))
      area += begin - list.shift();
  }
  return area;
}
