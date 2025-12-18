// inputに入力データ全体が入る
function Main(str) {
  const num = str.split('\s');
  const num1 = parseInt(num[0]);
  const num2 = parseInt(num[1]);

  const max = Math.max(num1 + num2, num1 - num2, num1 * num2);

  if (max === -0 || max === +0) {
    console.log(0);
  } else {
    console.log(max);
  }
}

//*この行以降は編集しないでください（標準入出力から一度に読み込み、Mainを呼び出します）
Main(require("fs").readFileSync("/dev/stdin", "utf8"));