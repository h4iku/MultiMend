Main =
    input => {
      input = input.split("\n");
      const tmp = input[0].split(" ");
      const n = tmp[0];
      const k = tmp[1];
      const h = input[1].split(" ");

      var cnt = 0;
      h.forEach(ht => {
        if (ht >= k) {
          cnt++;
        }
      });

      console.log(cnt);
    }

Main(require("fs").readFileSync("/dev/stdin", "utf8"));