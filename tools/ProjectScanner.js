// East SMP Website 2.0
// Advanced Project Scanner
// tools/ProjectScanner.js

import fs from "fs";
import { chromium } from "playwright";



const results = [];



function addResult(type, name, passed, details){

    results.push({
        type,
        name,
        passed:Boolean(passed),
        details
    });

}





function checkFile(file){

    const exists = fs.existsSync(file);

    addResult(
        "📁 Files",
        file,
        exists,
        exists
        ? "File exists"
        : "File missing"
    );

    return exists;

}





function scanFolder(folder){

    if(!fs.existsSync(folder)){

        return [];

    }


    return fs.readdirSync(
        folder,
        {
            recursive:true
        }
    );

}





// ==============================
// PROJECT FILES
// ==============================


console.log("\n📁 Checking important files...\n");


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


for(const file of importantFiles){

    checkFile(file);

}





// ==============================
// FOLDERS
// ==============================


console.log("\n📂 Checking folders...\n");


const folders = [

"src",

"src/pages",

"src/components",

"src/layouts",

"src/scripts",

"public",

"tools"

];


for(const folder of folders){

    const exists = fs.existsSync(folder);


    addResult(
        "📂 Folder",
        folder,
        exists,
        exists
        ? "Folder exists"
        : "Folder missing"
    );

}





const files = scanFolder("src");





// ==============================
// ASTRO SCAN
// ==============================


let astroCount = 0;


for(const file of files){

    if(file.endsWith(".astro")){

        astroCount++;

    }

}


addResult(

"⚡ Astro",

"Astro Components",

astroCount > 0,

`${astroCount} Astro files found`

);





// ==============================
// JS SCAN
// ==============================


let jsCount = 0;


for(const file of files){

    if(
        file.endsWith(".js") ||
        file.endsWith(".ts")
    ){

        jsCount++;

    }

}


addResult(

"🟨 JavaScript",

"Scripts Found",

jsCount > 0,

`${jsCount} JS/TS files found`

);





// ==============================
// CSS SCAN
// ==============================


let cssCount = 0;


for(const file of files){

    if(file.endsWith(".css")){

        cssCount++;

    }

}


addResult(

"🎨 CSS",

"Stylesheets",

cssCount > 0,

`${cssCount} CSS files found`

);







// ==============================
// WEBSITE TESTS
// ==============================


const WEBSITE = "http://localhost:4321";





// ==============================
// BROKEN LINK CHECK
// ==============================


async function checkLinks(){

    try{

        const browser =
        await chromium.launch();


        const page =
        await browser.newPage();


        await page.goto(WEBSITE);


        const links =
        await page.$$eval(
            "a",
            els =>
            els.map(
                e=>e.href
            )
        );


        let broken=[];


        for(const link of links){

            if(link.startsWith(WEBSITE)){


                const response =
                await fetch(link);


                if(!response.ok){

                    broken.push(link);

                }

            }

        }


        await browser.close();



        addResult(

        "🔗 Links",

        "Broken Link Scanner",

        broken.length===0,

        broken.length
        ? `${broken.length} broken links`
        : `${links.length} links checked`

        );


    }

    catch(error){

        addResult(
        "🔗 Links",
        "Broken Link Scanner",
        false,
        error.message
        );

    }

}





// ==============================
// CONSOLE ERRORS
// ==============================


async function checkConsole(){


    const browser =
    await chromium.launch();



    const page =
    await browser.newPage();



    let errors=[];



    page.on(
        "console",
        msg=>{

            if(msg.type()=="error"){

                errors.push(msg.text());

            }

        }
    );



    await page.goto(
        WEBSITE
    );



    await browser.close();



    addResult(

    "🖥️ Console",

    "Console Error Detector",

    errors.length===0,

    errors.length
    ? errors.join(", ")
    : "No console errors"

    );


}






// ==============================
// IMAGE CHECK
// ==============================


async function checkImages(){


    const browser =
    await chromium.launch();


    const page =
    await browser.newPage();


    await page.goto(
        WEBSITE
    );



    const broken =
    await page.$$eval(
        "img",
        imgs =>
        imgs
        .filter(
        img=>!img.complete ||
        img.naturalWidth===0
        )
        .map(
        img=>img.src
        )
    );



    await browser.close();



    addResult(

    "🖼️ Images",

    "Missing Image Detector",

    broken.length===0,

    broken.length
    ? `${broken.length} broken images`
    : "All images loaded"

    );


}







// ==============================
// MOBILE TEST
// ==============================


async function checkMobile(){


    const browser =
    await chromium.launch();



    const page =
    await browser.newPage({

        viewport:{
            width:390,
            height:844
        }

    });



    await page.goto(
        WEBSITE
    );



    const width =
    await page.evaluate(
        ()=>document.body.scrollWidth
    );



    await browser.close();



    addResult(

    "📱 Mobile",

    "Mobile Compatibility",

    width <= 390,

    width <= 390
    ? "Fits mobile screen"
    : "Horizontal scrolling detected"

    );


}





// ==============================
// SPEED TEST
// ==============================


async function checkSpeed(){


    const start =
    performance.now();



    await fetch(
        WEBSITE
    );



    const time =
    performance.now()-start;



    let rating =
    "Excellent";



    if(time>1000)
        rating="Slow";

    else if(time>500)
        rating="Good";



    addResult(

    "⚡ Speed",

    "Load Speed Rating",

    time<1500,

    `${Math.round(time)}ms - ${rating}`

    );


}







// ==============================
// VERSION CHECK
// ==============================


function versionCheck(){


    addResult(

    "🔢 Version",

    "Website Version",

    fs.existsSync("package.json"),

    "Version files detected"

    );


}





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


let passed = results.filter(
r=>r.passed
).length;



const score =
Math.round(
(passed/results.length)*100
);



console.log(
`
✅ WEBSITE HEALTH SCORE

${passed}/${results.length}

${score}%

==============================
`
);



fs.mkdirSync(
"reports",
{
recursive:true
}
);



fs.writeFileSync(

"reports/scanner.json",

JSON.stringify(
results,
null,
2
)

);



console.log(
"📄 Report saved: reports/scanner.json"
);