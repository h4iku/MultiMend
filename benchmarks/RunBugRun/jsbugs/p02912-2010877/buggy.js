'use strict';

const testcase = null;

function main(input) {
  const n = parseInt(input.shift());
  const m = parseInt(input.shift());
  const b = new BinaryHeap();
  for (var i = 0; i < n; i++) {
    b.push(parseInt(input.shift()));
  }
  console.log(b);
  for (var i = 0; i < m; i++) {
    b.push(b.pop() / 2);
    console.log(b);
  }
  var sum = 0;
  for (var i = 0; i < n; i++) {
    sum += Math.trunc(b.pop());
  }
  console.log(sum);
}

class BinaryHeap {
  constructor() {
    // HACK: first is unused
    this.heap = new Array(1);
  }
  push(data) {
    const index = this.heap.push(data) - 1;
    BinaryHeap.upHeap(this.heap, index);
  }
  static upHeap(heap, idx) {
    const parent = Math.trunc(idx / 2);
    if (heap[parent] < heap[idx]) {
      const tmp = heap[idx];
      heap[idx] = heap[parent];
      heap[parent] = tmp;
      BinaryHeap.upHeap(heap, parent);
    }
  }
  pop() {
    const index = 1;
    const data = this.heap[index];
    const last = this.heap.pop();
    if (1 < this.heap.length) {
      this.heap[index] = last;
      BinaryHeap.downHeap(this.heap, index);
    }
    return data;
  }
  static downHeap(heap, idx) {
    const childL = idx * 2, childR = idx * 2 + 1;
    var target = idx;
    target = heap[target] < heap[childL] ? childL : target;
    target = heap[target] < heap[childR] ? childR : target;
    if (target != idx) {
      const tmp = heap[target];
      [heap[target]] = heap[idx];
      heap[idx] = tmp;
      BinaryHeap.downHeap(heap, target);
    }
  }
}

// as python, if __name__ == '__main__':
if (process.argv[1] == __filename) {
  const input = testcase || require('fs').readFileSync('/dev/stdin', 'utf-8');
  main(input.split(/\s/));
}
