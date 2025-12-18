function Dice(labels) {
  this.top = labels[0];
  this.back = labels[1];
  this.right = labels[2];
  this.left = labels[3];
  this.front = labels[4];
  this.bottom = labels[5];
};

Dice.prototype.roll = function(direction) {
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
  }
};

Dice.prototype.rollToTop = function(top) {
  if (top === this.right) {
    this.roll('W');
  } else if (top === this.left) {
    this.roll('E');
  } else if (top === this.back) {
    this.roll('N');
  } else if (top === this.front) {
    this.roll('S');
  }
};

Dice.prototype.getRightWithTopAndBack = function(top, back) {
  if (top === this.top) {
    if (back === this.back) {
      return this.right;
    }
    if (back === this.left) {
      return this.back;
    }
    if (back === this.front) {
      return this.left;
    }
    if (back === this.right) {
      return this.front;
    }
  }
  if (top === this.front) {
    if (back === this.top) {
      return this.right;
    }
    if (back === this.left) {
      return this.top;
    }
    if (back === this.bottom) {
      return this.left;
    }
    if (back === this.right) {
      return this.bottom;
    }
  }
  if (top === this.bottom) {
    if (back === this.front) {
      return this.right;
    }
    if (back === this.left) {
      return this.front;
    }
    if (back === this.back) {
      return this.left;
    }
    if (back === this.right) {
      return this.back;
    }
  }
  if (top === this.back) {
    if (back === this.bottom) {
      return this.right;
    }
    if (back === this.left) {
      return this.bottom;
    }
    if (back === this.top) {
      return this.left;
    }
    if (back === this.right) {
      return this.top;
    }
  }
  if (top === this.right) {
    if (back === this.bottom) {
      return this.front;
    }
    if (back === this.back) {
      return this.bottom;
    }
    if (back === this.top) {
      return this.back;
    }
    if (back === this.front) {
      return this.top;
    }
  }
  if (top === this.left) {
    if (back === this.top) {
      return this.front;
    }
    if (back === this.front) {
      return this.bottom;
    }
    if (back === this.bottom) {
      return this.back;
    }
    if (back === this.back) {
      return this.top;
    }
  }
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