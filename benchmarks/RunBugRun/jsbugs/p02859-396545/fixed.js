function main(input) { console.log(input * input); }
main(require("fs").readFileSync("/dev/stdin", "utf8"));