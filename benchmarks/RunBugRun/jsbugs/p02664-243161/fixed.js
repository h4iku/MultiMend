function Main(t) {
  let characters = t.split("");
  for (let i = 0; characters[i]; i++)
    if (characters[i] == "?")
      characters[i] = "D";
  let joined = characters.join("");
  console.log(joined);
}
Main(require("fs").readFileSync("/dev/stdin", "utf8"));
