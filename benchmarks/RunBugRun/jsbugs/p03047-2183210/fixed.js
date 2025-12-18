function main(input) {
  var continuityNum = input.split(" ")[0];
  var selectNum = input.split(" ")[1];

  var nowNum = 1;
  var endFlg = 0;

  var count = 0;
  while (1) {
    var judge　= nowNum;
    if (Number(judge) + Number(selectNum) - 1 <= continuityNum) {
      nowNum++;
      count++;
    } else {
      console.log(count);
      break;
    }
  }
}

main(require('fs').readFileSync('/dev/stdin', 'utf8'));
