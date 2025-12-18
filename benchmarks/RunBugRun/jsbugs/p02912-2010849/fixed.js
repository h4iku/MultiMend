module.exports = function(t) {
  var e = {};
  function i(r) {
    if (e[r])
      return e[r].exports;
    var s = e[r] = {i : r, l : !1, exports : {}};
    return t[r].call(s.exports, s, s.exports, i), s.l = !0, s.exports
  }
  return i.m = t, i.c = e, i.d = function(t, e, r) {
    i.o(t, e) || Object.defineProperty(t, e, {enumerable : !0, get : r})
  }, i.r = function(t) {
    "undefined" != typeof Symbol && Symbol.toStringTag &&
        Object.defineProperty(t, Symbol.toStringTag, {value : "Module"}),
        Object.defineProperty(t, "__esModule", {value : !0})
  }, i.t = function(t, e) {
    if (1 & e && (t = i(t)), 8 & e)
      return t;
    if (4 & e && "object" == typeof t && t && t.__esModule)
      return t;
    var r = Object.create(null);
    if (i.r(r),
        Object.defineProperty(r, "default", {enumerable : !0, value : t}),
        2 & e && "string" != typeof t)
      for (var s in t)
        i.d(r, s, function(e) { return t[e] }.bind(null, s));
    return r
  }, i.n = function(t) {
    var e = t && t.__esModule ? function() { return t.default }
                              : function() { return t };
    return i.d(e, "a", e), e
  }, i.o = function(t, e) {
    return Object.prototype.hasOwnProperty.call(t, e)
  }, i.p = "", i(i.s = 0)
}([
  function(t, e, i) {
    "use strict";
    var r = i(1);
    i(2)(r.readFileSync("/dev/stdin", "utf8"))
  },
  function(t, e) { t.exports = require("fs") },
  function(t, e, i) {
    "use strict";
    var r = i(3), s = i(5);
    t.exports = function(t) {
      var e = new r(t);
      s(e)
    }
  },
  function(t, e, i) {
    "use strict";
    var r = i(4);
    t.exports = class {
      constructor(t) {
        var e = t.trim().split(/\s+/g);
        this.inp = new r(e)
      }
      inr() { return this.inp.deq() }
      in() { return parseInt(this.inp.deq(), 10) }
      fin() { this.inp.clear() }
    }
  },
  function(t, e, i) {
    "use strict";
    t.exports = class {
      constructor() {
        var t =
            arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : [];
        this.size = t.length, this.items = t, this.ind = 0
      }
      enq(t) { this.size += 1, this.items.push(t) }
      deq() {
        var t = this.items[this.ind];
        return this.size -= 1, this.ind += 1, t
      }
      clear() { this.items = [], this.size = 0, this.ind = 0 }
    }
  },
  function(t, e, i) {
    "use strict";
    var r = i(6);
    t.exports = function(t) {
      for (var e = t.in(), i = t.in(), s = new r, n = 0; n < e; n++) {
        var o = t.in();
        s.pushItem(o)
      }
      for (var h = 0; h < i; h++) {
        var a = s.getTop();
        s.removeTop(), s.pushItem(Math.floor(a / 2))
      }
      for (var u = 0, p = s.getValuesList(), f = 0; f < e; f++)
        u += p[f];
      console.log(u)
    }
  },
  function(t, e, i) {
    "use strict";
    function r(t, e) { return t <= e }
    function s(t, e) { return t >= e }
    t.exports = class {
      constructor() {
        var t = arguments.length > 0 && void 0 !== arguments[0] ? arguments[0]
                                                                : [],
            e = !(arguments.length > 1 && void 0 !== arguments[1]) ||
                arguments[1],
            i = arguments.length > 2 && void 0 !== arguments[2] ? arguments[2]
                                                                : void 0;
        this.cf = e ? r : s, i && (this.cf = i), this.heap = t,
        this.size = this.heap.length, this.heapify()
      }
      heapify() {
        for (var t = 0, e = this.size; 2 * t + 1 <= e;)
          t = 2 * t + 1;
        for (var i = t - 1; i >= 0;)
          2 * i + 1 > e - 1 ? i-- : (this.downHeap(i), i--)
      }
      downHeap(t) {
        for (var e = this.size, i = t; 2 * i + 1 < e;) {
          var r = this.heap[2 * i + 1],
              s = 2 * i + 2 < e ? this.heap[2 * i + 2] : r,
              n = this.cf(s, r) ? r : s,
              o = this.cf(s, r) ? 2 * i + 1 : 2 * i + 2;
          if (this.cf(n, this.heap[i]))
            break;
          var h = n;
          this.heap[o] = this.heap[i], this.heap[i] = h, i = o
        }
      }
      upHeap(t) {
        for (var e = t; 0 != e;) {
          var i = Math.floor((e - 1) / 2);
          if (this.cf(this.heap[e], this.heap[i]))
            break;
          var r = this.heap[i];
          this.heap[i] = this.heap[e], this.heap[e] = r, e = i
        }
      }
      pushItem(t) {
        this.size += 1, this.heap.push(t), this.upHeap(this.size - 1)
      }
      getTop() { return this.heap[0] }
      removeTop() {
        return 0 != this.size &&
               (1 == this.size
                    ? (this.size = 0, this.heap = [], !0)
                    : (this.size -= 1, this.heap[0] = this.heap.pop(),
                       this.downHeap(0), !0))
      }
      getValuesList() { return this.heap }
    }
  }
]);