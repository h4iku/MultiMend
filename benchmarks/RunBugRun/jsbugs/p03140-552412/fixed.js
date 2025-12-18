const main = n => {
  for (input = n.split("\n"), N = parseInt(input[0]), answer = 0,
      moto_word = [], i = 0;
       i < N; i++)
    answer += new Set([ input[1][i], input[2][i], input[3][i] ]).size - 1;
  console.log("%d", answer)
};
main(require("fs").readFileSync("/dev/stdin", "utf8"));