function PriorityQueue() { this.heap = []; }
PriorityQueue.prototype = {
  push : function(x) {
    var h = this.heap, i = h.length++, j;
    while (i) {
      j = i - 1 >> 1;
      if (h[j] <= x)
        break;
      h[i] = h[j];
      i = j;
    }
    h[i] = x;
  },
  pop : function() {
    var h = this.heap, r = h[0], x = h.pop();
    var i = 0, k = h.length >> 1, j;
    while (i < k) {
      j = (i << 1) + 1;
      if (h[j + 1] < h[j])
        ++j;
      if (x <= h[j])
        break;
      h[i] = h[j];
      i = j;
    }
    if (h.length)
      h[i] = x;
    return r;
  },
  size : function() { return this.heap.length; },
  top : function() { return this.heap[0]; },
};

function main(input) {
  var args = input.trim().split("\n");
  var info = args[0].split(" ").map((v) => parseInt(v));
  var N = info[0];                                     // 個数
  var M = info[1];                                     // 割引券
  var As = args[1].split(" ").map((v) => parseInt(v)); // 値段

  if (N === 1) {
    console.log(Math.floor(As[0] / Math.pow(2, M)));
    return;
  }

  var pq = new PriorityQueue();

  for (var i = 0; As.length > i; i++) {
    pq.push(-As[i]);
  }

  for (var j = 0; M > j; j++) {
    var max = -pq.pop();
    pq.push(-(Math.floor(max / 2)));
  }

  var result = 0;
  while (pq.size() > 0) {
    result += -pq.pop();
  }

  console.log(result);
}

main(require("fs").readFileSync("/dev/stdin", "utf8"));