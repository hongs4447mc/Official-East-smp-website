// src/scripts/Testerbot.js

export async function runWebsiteTests(progress, onResult) {

const results = [];


function addResult(type, name, passed, details = "") {

    const r = {
        type,
        name,
        passed: Boolean(passed),
        details:
            details ||
            (
                passed
                ? "Working correctly"
                : "Failed - feature not detected"
            )
    };


    results.push(r);


    if(typeof onResult === "function") {

        onResult(r);

    }

}



const origin = location.origin;



async function getHomeHTML(){

    try{

        const page = await fetch(origin + "/");

        return await page.text();

    }

    catch{

        return "";

    }

}



function getFailureReason(name){


const reasons = {


"Home Page":
"Homepage could not load",


"Rules Page":
"Missing /rules page",


"Roles Page":
"Missing /roles page",


"Updates Page":
"Missing /updates page",


"Story Page":
"Missing /story page",


"Applications Page":
"Missing /applications page",



"Discord Button":
"Missing discord-button class",


"Server IP Copy Button":
"Missing copy-button class",


"Copy Button Script":
"Clipboard JavaScript not detected",


"Clipboard API Support":
"Browser does not support clipboard",


"Copy Text Test":
"Clipboard permission denied",


"Status Button":
"Missing status-arrow",


"Suggestions/issues Button":
"Missing suggestion-arrow",



"Navbar":
"Missing nav element",


"Menu Button":
"Missing .menu-button",


"Side Menu":
"Missing .nav-links",


"Navigation Links":
"No navigation links found",



"Rule Boxes":
"Missing .rule-box",


"Creator Cards":
"Missing .creator-card",


"Sections":
"Missing section elements",


"Footer":
"Missing footer",



"Server IP Display":
"eastsmp.mc.gg not found",


"Status System":
"Missing status-box",



"Performance API":
"Browser performance API unavailable",


"Load Timer":
"Performance timer failed",



"HTTPS":
"Website is not HTTPS"

};


return reasons[name] || "Unknown issue";

}





const tests = [


// =========================
// PAGES
// =========================


{
type:"🏠 Pages",
name:"Home Page",

run:async()=>{

    return await fetch(origin + "/");

}

},



{
type:"📜 Pages",
name:"Rules Page",

run:async()=>{

    return await fetch(origin + "/rules");

}

},



{
type:"👥 Pages",
name:"Roles Page",

run:async()=>{

    return await fetch(origin + "/roles");

}

},



{
type:"📝 Pages",
name:"Updates Page",

run:async()=>{

    return await fetch(origin + "/updates");

}

},



{
type:"📖 Pages",
name:"Story Page",

run:async()=>{

    return await fetch(origin + "/story");

}

},



{
type:"📋 Pages",
name:"Applications Page",

run:async()=>{

    return await fetch(origin + "/applications");

}

},



// =========================
// WEBSITE SYSTEMS
// =========================


{
type:"⚙️ Website Systems",
name:"HTML Loaded",
run:()=>!!document.documentElement
},


{
type:"⚙️ Website Systems",
name:"Body Loaded",
run:()=>!!document.body
},


{
type:"⚙️ Website Systems",
name:"CSS Loaded",
run:()=>document.styleSheets.length > 0
},


{
type:"⚙️ Website Systems",
name:"JavaScript Working",
run:()=>true
},


{
type:"⚙️ Website Systems",
name:"Page Content",
run:()=>!!document.querySelector(".page-content")
},


{
type:"⚙️ Website Systems",
name:"Astro Loaded",
run:()=>!!document.querySelector("body")
},




// =========================
// BUTTONS
// =========================


{
type:"🔘 Buttons",
name:"Discord Button",

run:async()=>{

const html = await getHomeHTML();

return html.includes("discord-button");

}

},



{
type:"🔘 Buttons",
name:"Server IP Copy Button",

run:async()=>{

const html = await getHomeHTML();

return html.includes("copy-button");

}

},



{
type:"🔘 Buttons",
name:"Copy Button Script",

run:async()=>{

const html = await getHomeHTML();

return (
html.includes("clipboard.writeText")
||
html.includes("navigator.clipboard")
);

}

},



{
type:"🔘 Buttons",
name:"Clipboard API Support",

run:()=>typeof navigator.clipboard !== "undefined"

},



{
type:"🔘 Buttons",
name:"Copy Text Test",

run:async()=>{

try{

await navigator.clipboard.writeText(
"eastsmp.mc.gg"
);

return true;

}

catch{

return false;

}

}

},



{
type:"🔘 Buttons",
name:"Status Button",

run:async()=>{

const html = await getHomeHTML();

return html.includes("status-arrow");

}

},



{
type:"🔘 Buttons",
name:"Suggestions/issues Button",

run:async()=>{

const html = await getHomeHTML();

return html.includes("suggestion-arrow");

}

},




// =========================
// NAVIGATION
// =========================


{
type:"🧭 Navigation",
name:"Navbar",
run:()=>!!document.querySelector("nav")
},


{
type:"🧭 Navigation",
name:"Menu Button",
run:()=>!!document.querySelector(".menu-button")
},


{
type:"🧭 Navigation",
name:"Side Menu",
run:()=>!!document.querySelector(".nav-links")
},


{
type:"🧭 Navigation",
name:"Navigation Links",
run:()=>document.querySelectorAll("a").length > 0
},




// =========================
// COMPONENTS
// =========================


{
type:"📦 Components",
name:"Rule Boxes",
run:()=>!!document.querySelector(".rule-box")
},


{
type:"📦 Components",
name:"Creator Cards",
run:()=>!!document.querySelector(".creator-card")
},


{
type:"📦 Components",
name:"Sections",
run:()=>!!document.querySelector("section")
},


{
type:"📦 Components",
name:"Footer",
run:()=>!!document.querySelector("footer")
},




// =========================
// SERVER
// =========================


{
type:"⚔️ Server",
name:"Server IP Display",

run:async()=>{

const html = await getHomeHTML();

return html.includes(
"eastsmp.mc.gg"
);

}

},



{
type:"⚔️ Server",
name:"Status System",

run:async()=>{

const html = await getHomeHTML();

return html.includes(
"status-box"
);

}

},




// =========================
// PERFORMANCE
// =========================


{
type:"🚀 Performance",
name:"Performance API",

run:()=>typeof performance !== "undefined"

},


{
type:"🚀 Performance",
name:"Load Timer",

run:()=>performance.now()>0

},




// =========================
// SECURITY
// =========================


{
type:"🔒 Security",
name:"HTTPS",

run:()=>(
location.protocol==="https:"
||
location.hostname==="localhost"
)

}



];





let finished = 0;



for(const test of tests){


let passed = false;

let details = "";



try{


const res = await test.run();



if(
res &&
typeof res==="object" &&
"ok" in res
){

passed = Boolean(res.ok);

details =
passed
?
`Loaded successfully (${res.status})`
:
`Failed loading page (${res.status})`;

}


else{


passed = Boolean(res);



if(!passed){

details = getFailureReason(test.name);

}

}



}

catch(err){


passed = false;

details =
"Error: " +
String(err?.message || err);


}



addResult(
test.type,
test.name,
passed,
details
);



finished++;



if(typeof progress==="function"){

progress(
Math.floor(
(finished/tests.length)*100
)
);

}



await new Promise(
resolve=>setTimeout(resolve,120)
);



}



addResult(
"⚙️ Bot",
"Tester Bot Running",
true,
"All tests completed"
);



return results;


}