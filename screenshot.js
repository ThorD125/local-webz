const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');
const yargs = require('yargs');

// Parse command-line arguments
const argv = yargs
  .option('input', {
    alias: 'i',
    description: 'Path to a JSON file containing URLs',
    type: 'string',
  })
  .option('output', {
    alias: 'o',
    description: 'Directory to save screenshots',
    type: 'string',
  })
  .argv;

async function takeScreenshot(url, outputPath) {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();

  // Set viewport width to 1920px for the screenshot
  await page.setViewport({ width: 1920, height: 1080 });

  try {
    await page.goto(url, { waitUntil: 'load', timeout: 0 }); // Disable timeout
    await page.screenshot({ path: outputPath, fullPage: true });
    console.log(`Screenshot taken: ${url}`);
  } catch (error) {
    if (error.name === 'TimeoutError') {
      console.log(`Timeout error for: ${url}. Skipping.`);
    } else {
      console.error(`Error taking screenshot of ${url}:`, error);
    }
  } finally {
    await browser.close();
  }
}

function ensureHttpProtocol(url) {
  if (!/^https?:\/\//i.test(url)) {
    // Prepend 'https://' if no protocol is present
    return 'https://' + url;
  }
  return url;
}

async function screenshotFromUrls(urls, outputDir) {
  // Ensure output directory exists
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  for (let url of urls) {
    const formattedUrl = ensureHttpProtocol(url);  // Ensure URL has protocol
    const outputPath = path.join(outputDir, `${new URL(formattedUrl).hostname}.png`);
    console.log(`Processing: ${formattedUrl}`);
    await takeScreenshot(formattedUrl, outputPath);
  }
}

(async () => {
  const outputDir = argv.output || './output/screenshot';  // Default output directory

  if (argv.input) {
    const filePath = path.resolve(argv.input);
    if (fs.existsSync(filePath)) {
      const fileContent = fs.readFileSync(filePath, 'utf-8');
      const urls = JSON.parse(fileContent);

      if (Array.isArray(urls)) {
        await screenshotFromUrls(urls, outputDir);
      } else {
        console.error('The input file must contain an array of URLs.');
      }
    } else {
      console.error('The specified file does not exist.');
    }
  } else if (argv._.length > 0) {
    const urls = argv._;
    await screenshotFromUrls(urls, outputDir);
  } else {
    console.error('Please provide a URL or input file.');
  }
})();
