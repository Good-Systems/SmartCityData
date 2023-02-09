const puppeteer = require('puppeteer');
const chromium = require("chrome-aws-lambda");
var preview = false;

//console.log("Starting Puppeteer")
const run = async function(url) {
try {
    //console.log("Getting the HTML")
    const base_url = url.split("/")[0] + "//" + url.split("/")[2];
    
    const browser = await chromium.puppeteer.launch({
        args: chromium.args,
        defaultViewport: chromium.defaultViewport,
        executablePath: await chromium.executablePath,
        //headless: chromium.headless
        headless: true
    });

    const page = await browser.newPage();
    await page.goto(url, {
        waitUntil: "networkidle0",
        //timeout: 10
    })
    .catch((err) => console.log("error loading url", err));

    var html_loaded = await page.content();

    html_loaded = html_loaded.replace(/href="\//g, 'href="' + base_url + '/');
    html_loaded = html_loaded.replace(/src="\/api/g, 'src="' + base_url + '/api');
    html_loaded = html_loaded.replace(/src="\/javascripts/g, 'src="' + base_url + '/javascripts');
    html_loaded = html_loaded.replace("vendor.js", "");
    
    await browser.close();
    //In the future, I will keep the browser open and reuse it for the next request
    //This will make it significantly faster -Sean

    if (preview) {
        html_loaded = html_loaded.replace(/<div class="banner">[\s\S]*?<\/div>/g, "");
        html_loaded = html_loaded.replace(/<div class="mobile-menu">[\s\S]*?<\/div>/g, "");
        html_loaded = html_loaded.replace(/<footer[\s\S]*?<\/footer>/g, "");
        html_loaded = html_loaded.replace(/<header[\s\S]*?<\/header>/g, "");
        html_loaded = html_loaded.replace(/<nav[\s\S]*?<\/nav>/g, "");
        html_loaded = html_loaded.replace(/<a class="skip-links"[\s\S]*?<\/a>/g, "");
        html_loaded = html_loaded.replace(/<i><a[\s\S]*?page<\/a><\/i>/g, "");    
    }

    return html_loaded

} catch (error) {
    console.log("Failure to get the HTML")
    console.log(error)
    return error
}

}

//console.log("About to run Puppeteer")
var url = process.argv[2];

if (url.indexOf("?preview=true") > -1) {
    url = url.replace("?preview=true", "");
    preview = true;
}

run(url).then(html => console.log(html));