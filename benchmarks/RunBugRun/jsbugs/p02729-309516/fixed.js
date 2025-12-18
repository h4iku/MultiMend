const s_list = require('fs').readFileSync('/dev/stdin', 'utf8').split(' ');
const n_list = s_list.map(s => parseInt(s, 10));
const n = n_list[0];
const m = n_list[1];

const ans_n = n > 1 ? n * (n - 1) / 2 : 0
const ans_m = m > 1 ? m * (m - 1) / 2 : 0
const ans = ans_n + ans_m
console.log(ans)