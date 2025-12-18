function Main(input) {
  input = input.split("\n");
  tmp = input[0].split(" ");
  var a = tmp[0];
  var b = tmp[1];
  var s;
  if (a != "H") {
    if (b == "H") {
      s = "H";
    } else {
      s = "D";
    }

  } else {
    s = b;
  }
  console.log('%s', s);
}

// "実行する"ボタンを押した時に実行される関数 (デバッグ用)
function debug() {
  var input = document.getElementById("input").value;
  Main(input);
}
Main(require("fs").readFileSync("/dev/stdin", "utf8"));