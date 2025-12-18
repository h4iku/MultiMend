require("fs")
    .readFileSync("/dev/stdin", "utf8")
    .trim()
    .split('\n')
    .map(function(i) {
      for (a = [], j = 0; j <= 9; j++)
        if ((n = 1 << j) & i)
          a.push(n);
      console.log(a.join(' '))
    })