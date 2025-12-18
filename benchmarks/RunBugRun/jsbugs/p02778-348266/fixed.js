"use strict";
var __importStar = (this && this.__importStar) || function(mod) {
  if (mod && mod.__esModule)
    return mod;
  var result = {};
  if (mod != null)
    for (var k in mod)
      if (Object.hasOwnProperty.call(mod, k))
        result[k] = mod[k];
  result["default"] = mod;
  return result;
};
Object.defineProperty(exports, "__esModule", {value : true});
var fs = __importStar(require("fs"));
function main(args) {
  // sardine
  // xxxxxxx
  var result = '';
  for (var i = 0; i < args.length; i++) {
    result = result + 'x';
  }
  console.log(result);
}
main(fs.readFileSync('/dev/stdin', 'utf8'));
