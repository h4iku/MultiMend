function Dice(labels) {
  this.top = labels[0];
  this.back = labels[1];
  this.right = labels[2];
  this.left = labels[3];
  this.front = labels[4];
  this.bottom = labels[5];
};

Dice.prototype.turn = function(direction) {
  switch (direction) {
  case 'W':
    var tmp = this.left;
    this.left = this.top;
    this.top = this.right;
    this.right = this.bottom;
    this.bottom = tmp;
    break;
  case 'N':
    var tmp = this.front;
    this.front = this.top;
    this.top = this.back;
    this.back = this.bottom;
    this.bottom = tmp;
    break;
  case 'E':
    var tmp = this.right;
    this.right = this.top;
    this.top = this.left;
    this.left = this.bottom;
    this.bottom = tmp;
    break;
  case 'S':
    var tmp = this.back;
    this.back = this.top;
    this.top = this.front;
    this.front = this.bottom;
    this.bottom = tmp;
    break;
  case 'R':
    var tmp = this.right;
    this.right = this.front;
    this.front = this.left;
    this.left = this.back;
    this.back = tmp;
    break;
  case 'L':
    var tmp = this.left;
    this.left = this.front;
    this.front = this.right;
    this.right = this.back;
    this.back = tmp;
    break;
  }
};

Dice.prototype.clone = function() {
  return new Dice(
      [ this.top, this.back, this.right, this.left, this.front, this.bottom ]);
};

Dice.prototype.getRightWithTopAndBack = function(top, back) {
  var dice = this.clone();
  var turns = 'NEEEN'.split('');
  var i = 0;
  do {
    var j = 0;
    do {
      console.log(dice);
      if (dice.top === top && dice.back === back) {
        return dice.right;
      }
      dice.turn('R');
    } while (j++ < 3);
    dice.turn(turns[i]);
  } while (i++ < turns.length);
  return null;
};

(function(input) {
var p = input.split('\n');
var labels = p.shift().split(' ').map(Number);
var dice = new Dice(labels);
var n = Number(p.shift());
for (var i = 0; i < n; i++) {
  var ls = p.shift().split(' ').map(Number);
  var top = ls[0];
  var back = ls[1];
  console.log(dice.getRightWithTopAndBack(top, back));
}
})(require('fs').readFileSync('/dev/stdin', 'utf8'));