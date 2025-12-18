function main(input) {
  const result = input.split('\n');
  const answer = new Set(result.slice(1));
  console.log(answer.size);
}

main(require('fs').readFileSync('/dev/stdin', 'utf8'));