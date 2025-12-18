function Main(input) {
  var numbers = input.split(" ").map(x => Number(x));
  var flag = new Boolean(false);
  if (numbers[0] === numbers[1]) {
    if (numbers[0] != numbers[2]) {
      flag = true;
    }
  } else {
    if (numbers[1] === numbers[2]) {
      flag = true;
    } else {
      if (numbers[0] === numbers[2]) {
        flag = true;
      }
    }
  }
  if (flag === true) {
    console.log("Yes");
  } else {
    console.log("No");
  }
}

//*この行以降は編集しないでください（標準入出力から一度に読み込み、Mainを呼び出します）
Main(require("fs").readFileSync("/dev/stdin", "utf8"));