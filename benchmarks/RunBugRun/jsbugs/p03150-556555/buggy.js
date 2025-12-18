function Main(input) {
  var flag = false;
  if (input.substr(0, 7) == "keyence" || input.substr(-7) == "keyence") {
    flag = true;
  } else {
    input = input.split("");
    var p = 0
    if (input[0] == "k") {
      p = 1;
      if (input[1] == "e") {
        p = 2;
        if (input[2] == "y") {
          p = 3;
          if (input[3] == "e") {
            p = 4;
            if (input[4] == "n") {
              p = 5;
              if (input[5] == "c") {
                p = 6;
              }
            }
          }
        }
      }
    }
    var n = 0
    if (input[input.length - 1] == "e") {
      n = 1;
      if (input[input.length - 1 - 1] == "c") {
        n = 2;
        if (input[input.length - 1 - 2] == "n") {
          n = 3;
          if (input[input.length - 1 - 3] == "e") {
            n = 4;
            if (input[input.length - 1 - 4] == "y") {
              n = 5;
              if (input[input.length - 1 - 5] == "e") {
                n = 6;
              }
            }
          }
        }
      }
    }
    console.log((flag || p + n >= 7) ? "YES" : "NO")
  }
}
Main(require("fs").readFileSync("/dev/stdin", "utf8").trim());
