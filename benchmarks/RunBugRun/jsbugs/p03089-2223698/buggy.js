var obj = init();
Main();
function nextInt() { return myconv(next(), 1); }
function nextStrArray() { return myconv(next(), 2); } //半角スペース分割
function nextIntArray() { return myconv(next(), 4); } //半角スペース + 数値化
function nextCharArray() { return myconv(next(), 6); } // 1文字分割
function next() { return obj.next(); }
function hasNext() { return obj.hasNext(); }
function myin() {
  return require("fs").readFileSync("/dev/stdin", "utf8").trim().split("\n");
}
function init() {
  var inputFile = myin();
  var returnObj = {
    "list" : inputFile,
    "index" : 0,
    "max" : inputFile.length,
    "hasNext" : function() { return (this.index < this.max); },
    "next" : function() {
      if (!this.hasNext()) {
        return "";
      } else {
        var returnInput = this.list[this.index];
        this.index++;
        return returnInput;
      }
    }
  };
  return returnObj;
}
function myout(t) { console.log(t); }   //標準出力
function myerr(t) { console.error(t); } //標準エラー出力
//[no]要素の扱い。数値型
//不明値、異常時:引数そのまま返す　1:数値へ変換
// 2:半角SPで分割 4:半角SPで分割し、数値配列へ
// 6:1文字で分割  7:1文字で分割し、数値配列へ
// 8:半角SPで結合 9:改行で結合 0:文字なしで結合
function myconv(i, no) {
  try {
    switch (no) {
    case 1:
      return parseInt(i);
    case 2:
      return i.split(" ");
    case 4:
      return i.split(" ").map((a) => Number(a));
    case 6:
      return i.split("");
    case 7:
      return i.split("").map((a) => Number(a));
    case 8:
      return i.join(" ");
    case 9:
      return i.join("\n");
    case 0:
      return i.join("");
    default:
      return i;
    }
  } catch (e) {
    return i;
  }
}
function Main() {
  var N = nextInt();
  var list = nextIntArray();
  for (var i = 0; i < N; i++) {
    if (list[i] > (i + 1)) {
      // x番目にxを超える値があってはならない
      myout(-1);
      return;
    }
  }
  var output = [];
  var count = 0;
  while (list.length > 0) {
    if (list[count] == count + 1) {
      count++;
    } else {
      output.unshift(list[count - 1]);
      list.splice(count - 1, 1);
      // myerr(list.length + " " + count);
      count = 0;
    }
  }

  myout(myconv(output, 9));
}