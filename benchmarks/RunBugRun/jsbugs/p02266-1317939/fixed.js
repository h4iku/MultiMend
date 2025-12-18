var getPools = function(geo) {
  var downside = [];
  var pools = [];
  for (var i = 0; i < geo.length; i += 1) {
    if (geo[i] === '\\') {
      downside.push(i);
    } else if (geo[i] === '/' && downside.length > 0) {
      var d = downside.pop();
      var pool = i - d;
      while (pools.length > 0 && pools[pools.length - 1][0] > d) {
        pool += pools.pop()[1];
      }
      pools.push([ d, pool ]);
    }
  }
  return pools.length > 0 ? pools.map(function(p) { return p[1]; }) : [];
};

var stdin = require('fs').readFileSync('/dev/stdin', 'utf8');
stdin.split('\n').forEach(function(line) {
  if (line !== '') {
    var geo = line.trim();
    var pools = getPools(geo);
    var total =
        pools.length > 0 ? pools.reduce(function(a, b) { return a + b; }) : 0;
    console.log(total);
    pools.unshift(pools.length);
    console.log(pools.join(' '));
  }
});