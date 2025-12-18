function Main(input) {

  input = input.split("\n");
  data = input[0].split(" ");
  each_data = input[1].split(" ");

  var member_cnt = parseInt(data[0], 10);
  var max_hight = parseInt(data[1], 10);

  var parce_cnt = 0;

  for (var cnt = 0; cnt < member_cnt; cnt++) {
    if (max_hight <= parceInt(each_data[cnt])) {
      parce_cnt++;
    }
  }

  console.log(parce_cnt);
}
//*この行以降は編集しないでください（標準入出力から一度に読み込み、Mainを呼び出します）
Main(require("fs").readFileSync("/dev/stdin", "utf8"));