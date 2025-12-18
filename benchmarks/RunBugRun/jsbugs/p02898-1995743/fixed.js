Main =
    input => {
      input = input.split("\n");
      const tmp = input[0].split(" ");
      const n = Number(tmp[0]);
      const k = Number(tmp[1]);
      const h = input[1].split(" ").map(ht => Number(ht));

      var cnt = 0;
      h.forEach(ht => {
        if (ht >= k) {
          cnt++;
        }
      });

      console.log(cnt);
    }

Main(require("fs").readFileSync("/dev/stdin", "utf8"));