"use strict";
process.stdin.resume();
process.stdin.setEncoding("utf8");

var reader = require("readline").createInterface({
  input : process.stdin,
  output : process.stdout
});

reader.on("line", line => {
  let word = line;
  let len = word.length - 1;
  let arr = [ "k", "e", "y", "e", "n", "c", "e" ];
  let keyence = "keyence";

  if (word.indexOf("keyence") == 0 || word.lastIndexOf("keyence") == len - 6) {
    console.log("YES");
    return;
  }

  let str = "";
  let ans = false;
  for (let i = 0; i < 6; i++) {
    str += arr.shift();
    let tmp = keyence.slice(i + 1);
    let index = word.indexOf(str)

    if (index == 0 && word.lastIndexOf(tmp) == len - (tmp.length - 1)) {
      ans = true;
      break;
    }
  }

  if (ans)
    console.log("YES");
  else
    console.log("NO");
});
