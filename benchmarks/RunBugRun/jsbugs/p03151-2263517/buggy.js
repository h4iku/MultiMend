function Main(input) {
  input = input.split("\n");
  N = parseInt(input[0]);
  A = new Array(N);
  B = new Array(N);
  C = new Array(N);
  tmpa = input[1].split(" ");
  tmpb = input[2].split(" ");
  list = new Array();
  var s = 0;
  var ans = 0;
  for (var i = 0; i < N; i++) {
    A[i] = parseInt(tmpa[i]);
    B[i] = parseInt(tmpb[i]);
    if (A[i] - B[i] > 0) {
      list.push(A[i] - B[i]);
    } else {
      s += Math.min(0, A[i] - B[i]);
      ans++;
    }
  }
  s = -s;
  list.sort(function(a, b) { return (b - a); });
  var s2 = 0;
  for (var i = 0; i < list.length; i++) {
    s2 += list[i];
    if (s2 >= s) {
      ans += i + 1;
      break;
    } else if (i == list.length - 1) {
      ans = -1;
    }
  }

  console.log('%s', ans);
}

// "実行する"ボタンを押した時に実行される関数 (デバッグ用)
function debug() {
  var input = document.getElementById("input").value;
  Main(input);
}
Main(require("fs").readFileSync("/dev/stdin", "utf8"));