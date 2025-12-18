var hoge = require('fs').readFileSync('/dev/stdin', 'utf8');
var init = hoge.split('\n');
for (var i = 0, iz = init.length; i < iz; i++) {
  if (init[i] == 0)
    break;
  var num = i + 1;
  console.log('Case ' + num + ': ' + init[i]);
}