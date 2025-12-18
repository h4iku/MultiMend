// Don't have to see. start------------------------------------------
var read = require('readline').createInterface({
  input : process.stdin,
  output : process.stdout
});
var obj;
var inLine = [];
read.on('line', function(input) { inLine.push(input); });
read.on('close', function() {
  obj = init(inLine);
  console.error('\n↑入力 ↓出力');
  Main();
});
function makeClone(obj) {
  return (obj instanceof Set) ? new Set(Array.from(obj))
                              : JSON.parse(JSON.stringify(obj));
}
function nextInt() { return myconv(next(), 1); }
function nextStrArray() { return myconv(next(), 2); }
function nextIntArray() { return myconv(next(), 4); }
function nextCharArray() { return myconv(next(), 6); }
function next() { return obj.next(); }
function hasNext() { return obj.hasNext(); }
function init(input) {
  return {
    list : input,
    index : 0,
    max : input.length,
    hasNext : function() { return (this.index < this.max); },
    next : function() {
      if (this.hasNext()) {
        return this.list[this.index++];
      } else {
        throw 'ArrayIndexOutOfBoundsException ‚There is no more input';
      }
    }
  };
}
function myout(s) { console.log(s); }
function myerr(s) {
  console.error('debug:' + require('util').inspect(s, false, null));
}
// param "no" is
// unknown or outlier : return i. 1: parseInt.
// 2: split space. 4: split space and parseInt.
// 6: split 1 character. 7: split 1 character and parseInt.
// 8: join space. 9: join nextline. 0: join no character.
function myconv(i, no) {
  try {
    switch (no) {
    case 1:
      return parseInt(i);
    case 2:
      return i.split(' ');
    case 4:
      return i.split(' ').map(Number);
    case 6:
      return i.split('');
    case 7:
      return i.split('').map(Number);
    case 8:
      return i.join(' ');
    case 9:
      return i.join('\n');
    case 0:
      return i.join('');
    default:
      return i;
    }
  } catch (e) {
    return i;
  }
}

// Don't have to see. end------------------------------------------
function Main() {
  var N = nextInt();
  var map = {};
  var aused = new Set();
  var bused = new Set();
  var alist = new Array(N); // red
  var blist = new Array(N); // blue
  for (var i = 0; i < N; i++) {
    var tmp = nextIntArray();
    alist[i] = {no : i, child : [], x : tmp[0], y : tmp[1]};
  }
  for (var i = 0; i < N; i++) {
    var tmp = nextIntArray();
    blist[i] = {no : i, child : [], x : tmp[0], y : tmp[1]};
  }
  for (var i = 0; i < N; i++) {
    for (var j = 0; j < N; j++) {
      if (alist[j].x < blist[i].x && alist[j].y < blist[i].y) {
        blist[i].child.push(j);
      }
    }
    blist[i].child.sort(function(a, b) { return alist[b].y - alist[a].y; });
  }
  blist.sort(function() { return a.child.length - b.child.length; });
  // myerr(blist);
  // return;

  for (var i = 0; i < N; i++) {
    var child = blist[i].child;
    for (var j = 0; j < child.length; j++) {
      if (!aused.has(child[j])) {
        aused.add(child[j]);
        break;
      }
    }
  }

  myout(aused.size);
}
