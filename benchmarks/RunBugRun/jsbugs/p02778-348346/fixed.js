console.log(
    require("fs").readFileSync("/dev/stdin", "utf8").replace(/./g, "x"));