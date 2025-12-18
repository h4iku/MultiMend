// inputに入力データ全体が入る
function Main(input) {
  var line = input.split("\n");
  var c = [];
  c[0] = line[0].split(" ");
  c[1] = line[1].split(" ");
  c[2] = line[2].split(" ");
  var sum = 0;
  for (var i = 0; i < c.length; i++) {
    for (var j = 0; j < c[i].length; j++) {
      c[i][j] = Number(c[i][j]);
      sum += c[i][j];
    }
  }
  if (sum % 3 !== 0) {
    console.log('No');
  } else {
    var difcol = [ c[0][1] - c[0][0], c[0][2] - c[0][1] ];
    var difrow = [ c[1][0] - c[0][0], c[2][0] - c[1][0] ];
    if (c[1][1] - c[1][0] !== difcol[0] || c[1][2] - c[1][0] !== difcol[1]) {
      console.log('No');
    } else if (c[2][1] - c[2][0] !== difcol[0] ||
               c[2][2] - c[2][1] !== difcol[1]) {
      console.log('No');
    } else if (c[1][1] - c[0][1] !== difrow[0] ||
               c[2][1] - c[1][1] !== difrow[1]) {
      console.log('No');
    } else if (c[1][2] - c[0][2] !== difrow[0] ||
               c[2][2] - c[1][2] !== difrow[1]) {
      console.log('No');
    } else {
      console.log('Yes');
    }
  }
}

//*この行以降は編集しないでください（標準入出力から一度に読み込み、Mainを呼び出します）
Main(require("fs").readFileSync("/dev/stdin", "utf8"));