#!/usr/bin/env node
const path = require("path"); const fs = require("fs"); const { chromium } = require("playwright-core");
const root = path.resolve(__dirname, ".."); const evidence = process.env.EVIDENCE_DIR || path.join(root, "evidence"); const url = process.env.SITE_URL || "http://127.0.0.1:8088/";
const cases = [{name:"360",width:360,height:800},{name:"390",width:390,height:844},{name:"768",width:768,height:1024},{name:"1280",width:1280,height:900}];
(async()=>{ fs.mkdirSync(evidence,{recursive:true}); const browser=await chromium.launch({executablePath:"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",headless:true});
for(const item of cases){ const page=await browser.newPage({viewport:{width:item.width,height:item.height}}); const errors=[]; page.on("pageerror",e=>errors.push(e.message)); page.on("console",m=>{if(m.type()==="error")errors.push(m.text())}); await page.goto(url,{waitUntil:"networkidle"});
await page.evaluate(async()=>{document.documentElement.style.scrollBehavior="auto";document.querySelectorAll('img[loading="lazy"]').forEach(img=>img.loading="eager");for(let y=0;y<document.documentElement.scrollHeight;y+=Math.max(350,innerHeight*.7)){scrollTo(0,y);await new Promise(r=>setTimeout(r,70))}await Promise.all(Array.from(document.images).map(img=>img.decode().catch(()=>{})));scrollTo(0,0);await new Promise(r=>setTimeout(r,250))});
await page.screenshot({path:path.join(evidence,`screenshot-${item.name}.png`),fullPage:true}); if(errors.length)throw new Error(`${item.name}: ${errors.join(" | ")}`); console.log(`PASS: screenshot ${item.name}px`); await page.close(); }
await browser.close(); console.log("VERDICT: PASS"); })().catch(e=>{console.error(`FAIL: ${e.message}`);process.exit(1)});
