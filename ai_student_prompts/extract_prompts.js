// Extract GRADES + PROMPTS from a prompt_studio.html into prompts.json.
// Usage: node extract_prompts.js [input.html] [output.json]
const fs=require("fs"), path=require("path");
const inp=process.argv[2]||path.join(__dirname,"prompt_studio.html");
const out=process.argv[3]||path.join(__dirname,"prompts.json");
const html=fs.readFileSync(inp,"utf8");
const start=html.indexOf("const GRADES"), marker=html.indexOf("/* ---------- app");
if(start<0||marker<0) throw new Error("markers not found");
const sandbox={};
new Function("out", html.slice(start,marker)+"\nout.PROMPTS=PROMPTS;")(sandbox);
fs.writeFileSync(out, JSON.stringify(sandbox.PROMPTS,null,1));
console.log("wrote",out,":",sandbox.PROMPTS.length,"prompts");
