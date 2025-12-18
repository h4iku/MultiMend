function Main(input) {
  const data = input;

  var nums = data.split("");

  var sum = 0;

  for (var bit = 0; bit < 1 << (nums.length - 1); bit++) {
    var tempStr = [ nums[0] ];
    for (var i = 0; i < nums.length - 1; i++) {
      const num = nums[i + 1];
      if (bit & (1 << i)) {
        //フラグが立っていたら
        tempStr.push(num);
      } else {
        tempStr[tempStr.length - 1] += num; //文字連結
      }
    }
    sum += tempStr.reduce((p, c) => p + parseInt(c), 0);
  }

  console.log(sum);
}

Main(require("fs").readFileSync("/dev/stdin", "utf8"));
