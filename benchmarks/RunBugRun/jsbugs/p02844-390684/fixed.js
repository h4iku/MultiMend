// SMPG2019 - D
function main(input) {
  var inputs = input.split('\n');
  var n = parseInt(inputs[0]);
  var s = inputs[1].split('').map((n) => parseInt(n, 10));

  var candidacies = [];
  for (var i = 0; i < 1000; i++) {
    candidacies.push(`00${i}`.slice(-3).split('').map((n) => parseInt(n, 10)));
  }

  var whereDisappear = [];
  for (var i = 0; i < 10; i++) {
    whereDisappear.push([]);
  }
  s.forEach((char, i) => { whereDisappear[char].push(i); });

  var counter = 0;
  candidacies.forEach((candidacy) => {
    var tempWhere = -1;
    var isOk = true;
    candidacy.forEach((cNumber) => {
      tempWhere = whereDisappear[cNumber].find((n) => n > tempWhere);
      if (typeof tempWhere === 'undefined') {
        isOk = false;
        return;
      } else {
        isOk = true;
      }
    });
    if (isOk) {
      counter += 1;
    }
  });
  console.log(counter);
}
main(require('fs').readFileSync('/dev/stdin', 'utf8'));
