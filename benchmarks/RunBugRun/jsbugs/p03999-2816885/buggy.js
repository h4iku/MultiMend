process.stdin.resume();
process.stdin.setEncoding('ascii');

var input_stdin = "";
var input_stdin_array = "";
var input_currentline = 0;

process.stdin.on('data', function(data) { input_stdin += data; });

process.on('SIGINT', function() {
  input_stdin_array = input_stdin.split("\n");
  main();
  process.exit();
});

process.stdin.on('end', function() {
  input_stdin_array = input_stdin.split("\n");
  main();
});

function readLine() { return input_stdin_array[input_currentline++]; }

/////////////// ignore above this line ////////////////////

function main() {
  /*reading input*/
  var num = readLine();

  /* for avoiding \r at the end of the string */
  num = num.substr(0, num.length - 1);
  var ans = 0;

  function backtrack(s, sum) {
    if (s.length == 0) {
      ans += sum;
      return;
    }
    for (var i = 1; i <= s.length; i++) {
      var s1 = s.substr(0, i);
      var s2 = s.substr(i);
      // console.log(s1 + " " + s2);
      backtrack(s2, sum + parseInt(s1));
    }
  }

  backtrack(num, 0);
  console.log(ans.toString());
}
