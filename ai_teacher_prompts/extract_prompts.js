// Extract the GRADES + PROMPTS arrays from prompt_studio.html into prompts.json
// (single source of truth: the HTML tool). Run: node extract_prompts.js
const fs = require("fs");
const path = require("path");
const html = fs.readFileSync(path.join(__dirname, "prompt_studio.html"), "utf8");
const start = html.indexOf("const GRADES");
const marker = html.indexOf("/* ---------- app");
if (start < 0 || marker < 0) throw new Error("markers not found");
const js = html.slice(start, marker);
const sandbox = {};
new Function("out", js + "\nout.PROMPTS = PROMPTS; out.GRADES = GRADES;")(sandbox);
fs.writeFileSync(path.join(__dirname, "prompts.json"), JSON.stringify(sandbox.PROMPTS, null, 1));
console.log("wrote prompts.json:", sandbox.PROMPTS.length, "prompts");
