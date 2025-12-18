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

Dice.prototype.isEqual = function(other) {
  return this.top == other.top && this.back == other.back &&
         this.right == other.right && this.left == other.left &&
         this.front == other.front && this.bottom == other.bottom;
};

Dice.prototype.isEqualLabels = function(other) {
  var dice = this.clone();
  var turns = 'NEEEN'.split('');
  var i = 0;
  do {
    var j = 0;
    do {
      if (dice.isEqual(other)) {
        return true;
      }
      dice.turn('R');
    } while (j++ < 3);
    dice.turn(turns[i]);
  } while (i++ < turns.length);
  return false;
};

Dice.prototype.getRightWithTopAndBack = function(top, back) {
  var dice = this.clone();
  var turns = 'NEEEN'.split('');
  var i = 0;
  do {
    var j = 0;
    do {
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
var n = Number(p.shift());
var dices = [];
for (var i = 0; i < n; i++) {
  var labels = p.shift().split(' ').map(Number);
  var dice = new Dice(labels);
  dices.push(dice);
}
for (var i = 0; i < n; i++) {
  for (var j = i + 1; j < n; j++) {
    if (dices[i].isEqualLabels(dices[j])) {
      console.log('No');
      return;
    }
  }
}
console.log('Yes!');
})(require('fs').readFileSync('/dev/stdin', 'utf8'));