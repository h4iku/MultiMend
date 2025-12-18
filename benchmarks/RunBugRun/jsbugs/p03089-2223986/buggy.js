module.exports = function(e) {
  var t = {};
  function r(n) {
    if (t[n])
      return t[n].exports;
    var o = t[n] = {i : n, l : !1, exports : {}};
    return e[n].call(o.exports, o, o.exports, r), o.l = !0, o.exports
  }
  return r.m = e, r.c = t, r.d = function(e, t, n) {
    r.o(e, t) || Object.defineProperty(e, t, {enumerable : !0, get : n})
  }, r.r = function(e) {
    "undefined" != typeof Symbol && Symbol.toStringTag &&
        Object.defineProperty(e, Symbol.toStringTag, {value : "Module"}),
        Object.defineProperty(e, "__esModule", {value : !0})
  }, r.t = function(e, t) {
    if (1 & t && (e = r(e)), 8 & t)
      return e;
    if (4 & t && "object" == typeof e && e && e.__esModule)
      return e;
    var n = Object.create(null);
    if (r.r(n),
        Object.defineProperty(n, "default", {enumerable : !0, value : e}),
        2 & t && "string" != typeof e)
      for (var o in e)
        r.d(n, o, function(t) { return e[t] }.bind(null, o));
    return n
  }, r.n = function(e) {
    var t = e && e.__esModule ? function() { return e.default }
                              : function() { return e };
    return r.d(t, "a", t), t
  }, r.o = function(e, t) {
    return Object.prototype.hasOwnProperty.call(e, t)
  }, r.p = "", r(r.s = 0)
}([
  function(e, t,
           r) { r(1)(r(2).readFileSync("/dev/stdin", "UTF-8").split("\n")) },
  function(e, t, r) {
    "use strict";
    e.exports = function(e) {
      Number(e[0]);
      for (var t = e[1].split(" ")
                       .map(function(e) { return Number(e) })
                       .join(""),
               r = [];
           t.length > 0;) {
        for (var n = t.length, o = -1, u = 0; u < n; u++)
          t[u] == u + 1 && (o = u);
        if (-1 == o)
          return void console.log(-1);
        r.push(t[o]), t = t.slice(0, o) + t.slice(o + 1)
      }
      for (; r.length > 0;)
        console.log(r.pop())
    }
  },
  function(e, t) { e.exports = require("fs") }
]);