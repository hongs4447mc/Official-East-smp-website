
// East SMP Website 2.0
// Advanced Project Scanner
// tools/ProjectScanner.js

import fs from "fs";
import { chromium } from "playwright";

const results = [];

function addResult(type, name, passed, details) {
    results.push({
        type,
        name,
        passed: Boolean(passed),
        details
    });
}

function checkFile(file) {
    const exists = fs.existsSync(file);

    addResult(
        "Files",
        file,
        exists,
        exists ? "File exists" : "File missing"
    );

    return exists;
}

function scanFolder(folder) {
    if (!fs.existsSync(folder)) {
        return [];
    }

    return fs.readdirSync(folder, {
        recursive: true
    });
}

// ==============================
// PROJECT FILES
// ==============================

console.log("\nChecking important files...\n");

const importantFiles = [
    "package.json",
    "astro.config.mjs",
    "src/pages/index.astro",
    "src/pages/rules.astro",
    "src/pages/roles.astro",
    "src/pages/updates.astro",
    "src/pages/story.astro",
    "src/pages/applications.astro",
    "src/layouts/layout.astro",
    "src/styles/styles.css"
];

for (const file of importantFiles) {
    checkFile(file);
}

// ==============================
// FOLDERS
// ==============================

console.log("\nChecking folders...\n");

const folders = [
    "src",
    "src/pages",
    "src/components",
    "src/layouts",
    "src/scripts",
    "public",
    "tools"
];

for (const folder of folders) {
    const exists = fs.existsSync(folder);

    addResult(
        "Folder",
        folder,
        exists,
        exists ? "Folder exists" : "Folder missing"
    );
}

const files = scanFolder("src");

// ==============================
// ASTRO SCAN
// ==============================

let astroCount = 0;

for (const file of files) {
    if (file.endsWith(".astro")) {
        astroCount++;
    }
}

addResult(
    "Astro",
    "Astro Components",
    astroCount > 0,
    `${astroCount} Astro files found`
);

// ==============================
// JS / TS SCAN
// ==============================

let jsCount = 0;

for (const file of files) {
    if (
        file.endsWith(".js") ||
        file.endsWith(".ts")
    ) {
        jsCount++;
    }
}

addResult(
    "JavaScript",
    "Scripts Found",
    jsCount > 0,
    `${jsCount} JS/TS files found`
);

// ==============================
// CSS SCAN
// ==============================

let cssCount = 0;

for (const file of files) {
    if (file.endsWith(".css")) {
        cssCount++;
    }
}

addResult(
    "CSS",
    "Stylesheets",
    cssCount > 0,
    `${cssCount} CSS files found`
);

// ==============================
// WEBSITE TESTS
// ==============================

const WEBSITE = "http://localhost:4321/Official-East-smp-website";

// ==============================
// BROKEN LINK CHECK
// ==============================

async function checkLinks() {
    let browser;

    try {
        browser = await chromium.launch();

        const page = await browser.newPage();

        await page.goto(WEBSITE, {
            waitUntil: "networkidle"
        });

        const links = await page.$$eval(
            "a",
            elements => elements.map(element => element.href)
        );

        const broken = [];

        for (const link of links) {
            if (link.startsWith(WEBSITE)) {
                try {
                    const response = await fetch(link);

                    if (!response.ok) {
                        broken.push(link);
                    }
                } catch {
                    broken.push(link);
                }
            }
        }

        addResult(
            "Links",
            "Broken Link Scanner",
            broken.length === 0,
            broken.length === 0
                ? `${links.length} links checked`
                : `${broken.length} broken links: ${broken.join(", ")}`
        );
    } catch (error) {
        addResult(
            "Links",
            "Broken Link Scanner",
            false,
            error instanceof Error
                ? error.message
                : String(error)
        );
    } finally {
        if (browser) {
            await browser.close();
        }
    }
}

// ==============================
// CONSOLE / 404 CHECK
// ==============================

async function checkConsole() {
    let browser;

    try {
        browser = await chromium.launch();

        const page = await browser.newPage();

        const errors = [];

        page.on("response", response => {
            if (
                response.status() === 404 &&
                response.url() !== WEBSITE
            ) {
                errors.push(`404: ${response.url()}`);
            }
        });

        page.on("console", message => {
            if (message.type() === "error") {
                errors.push(`Console error: ${message.text()}`);
            }
        });

        await page.goto(WEBSITE, {
            waitUntil: "networkidle"
        });

        addResult(
            "Console",
            "Console Error Detector",
            errors.length === 0,
            errors.length === 0
                ? "No console errors or 404 resources detected"
                : errors.join(" | ")
        );
    } catch (error) {
        addResult(
            "Console",
            "Console Error Detector",
            false,
            error instanceof Error
                ? error.message
                : String(error)
        );
    } finally {
        if (browser) {
            await browser.close();
        }
    }
}

// ==============================
// IMAGE CHECK
// ==============================

async function checkImages() {
    let browser;

    try {
        browser = await chromium.launch();

        const page = await browser.newPage();

        await page.goto(WEBSITE, {
            waitUntil: "networkidle"
        });

        const broken = await page.$$eval(
            "img",
            images =>
                images
                    .filter(
                        image =>
                            !image.complete ||
                            image.naturalWidth === 0
                    )
                    .map(image => image.src)
        );

        addResult(
            "Images",
            "Missing Image Detector",
            broken.length === 0,
            broken.length === 0
                ? "All images loaded"
                : `${broken.length} broken images: ${broken.join(", ")}`
        );
    } catch (error) {
        addResult(
            "Images",
            "Missing Image Detector",
            false,
            error instanceof Error
                ? error.message
                : String(error)
        );
    } finally {
        if (browser) {
            await browser.close();
        }
    }
}

// ==============================
// MOBILE TEST
// ==============================

async function checkMobile() {
    let browser;

    try {
        browser = await chromium.launch();

        const page = await browser.newPage({
            viewport: {
                width: 390,
                height: 844
            }
        });

        await page.goto(WEBSITE, {
            waitUntil: "networkidle"
        });

        const width = await page.evaluate(
            () => document.body.scrollWidth
        );

        addResult(
            "Mobile",
            "Mobile Compatibility",
            width <= 390,
            width <= 390
                ? "Fits mobile screen"
                : `Horizontal scrolling detected: ${width}px`
        );
    } catch (error) {
        addResult(
            "Mobile",
            "Mobile Compatibility",
            false,
            error instanceof Error
                ? error.message
                : String(error)
        );
    } finally {
        if (browser) {
            await browser.close();
        }
    }
}

// ==============================
// SPEED TEST
// ==============================

async function checkSpeed() {
    try {
        const start = performance.now();

        const response = await fetch(WEBSITE);

        const time = performance.now() - start;

        let rating = "Excellent";

        if (time > 1000) {
            rating = "Slow";
        } else if (time > 500) {
            rating = "Good";
        }

        addResult(
            "Speed",
            "Load Speed Rating",
            response.ok && time < 1500,
            `${Math.round(time)}ms - ${rating}`
        );
    } catch (error) {
        addResult(
            "Speed",
            "Load Speed Rating",
            false,
            error instanceof Error
                ? error.message
                : String(error)
        );
    }
}

// ==============================
// VERSION CHECK
// ==============================

function versionCheck() {
    addResult(
        "Version",
        "Website Version",
        fs.existsSync("package.json"),
        "package.json detected"
    );
}

// ==============================
// RUN SCANNER
// ==============================

await checkLinks();
await checkConsole();
await checkImages();
await checkMobile();
await checkSpeed();

versionCheck();

// ==============================
// REPORT
// ==============================

console.log("\n==============================");

const passed = results.filter(
    result => result.passed
).length;

const score = Math.round(
    (passed / results.length) * 100
);

console.log(`
WEBSITE HEALTH SCORE

${passed}/${results.length}

${score}%

==============================
`);

fs.mkdirSync("reports", {
    recursive: true
});

fs.writeFileSync(
    "reports/scanner.json",
    JSON.stringify(results, null, 2)
);

console.log(
    "Report saved: reports/scanner.json"
);

