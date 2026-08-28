#!/usr/bin/env node
const crypto = require("crypto");
const { chromium } = require("playwright-core");
const beforeUrl = process.argv[2] || "http://127.0.0.1:8089/";
const afterUrl = process.argv[3] || "http://127.0.0.1:8088/";
const selectors = ["#included", "#details", "#disclosures", "#contact", "footer"];
const normalize = (value) => value.replace(/\s+/g, " ").trim();
const hash = (value) => crypto.createHash("sha256").update(value).digest("hex");
(async () => {
  const browser = await chromium.launch({ executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", headless: true });
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  const captures = {};
  for (const [label, url] of [["before", beforeUrl], ["after", afterUrl]]) {
    await page.goto(url, { waitUntil: "networkidle" });
    captures[label] = {};
    for (const selector of selectors) captures[label][selector] = normalize(await page.locator(selector).innerText());
  }
  await browser.close();
  for (const selector of selectors) {
    const before = captures.before[selector], after = captures.after[selector];
    console.log(`${selector}\tbefore_bytes=${Buffer.byteLength(before)}\tafter_bytes=${Buffer.byteLength(after)}\tbefore_sha256=${hash(before)}\tafter_sha256=${hash(after)}`);
    if (before !== after) throw new Error(`rendered protected text differs for ${selector}`);
    console.log(`PASS: rendered protected text unchanged for ${selector}`);
  }
  console.log("VERDICT: PASS — rendered disclosure text and SHA-256 hashes match across commits");
})().catch((error) => { console.error(`FAIL: ${error.message}`); process.exit(1); });
