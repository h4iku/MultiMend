"use strict"

const main =
    arg => {
      arg = arg.trim().split("\n");
      const N = parseInt(arg[0]);
      const s = arg[1].split(" ").map(n => parseInt(n));

      const points = [ 0, ...s, 0 ];
      const diff = [];
      const answer = [];

      points.forEach((p, i, self) => {
        if (i < self.length - 1)
          diff.push(self[i + 1] - self[i]);
      });

      const sum = diff.map(n => Math.abs(n)).reduce((a, b) => a + b);

      for (let i = 1; i < points.length - 1; i++) {
        const skipped = Math.abs(points[i - 1] - points[i + 1]);
        const stepped = Math.abs(points[i - 1] - points[i]) +
                        Math.abs(points[i] - points[i + 1]);

        const changed = skipped - stepped;

        answer.push(sum + changed);
      }

      console.log(answer.join("\n"));
    }

main(require("fs").readFileSync("/dev/stdin", "utf8"));
