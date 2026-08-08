/* =========================================================
   EAST SMP ASTRO JAVASCRIPT
   GitHub Pages + Astro Compatible
   ========================================================= */

console.log("✅ EASTSMP.JS IS RUNNING");


/* =========================================================
   WEBSITE SETTINGS
   ========================================================= */

const websiteSettings = {

    version: "Version 2.0",

    serverIP: "eastsmp.mc.gg"

};


let lastCheckTime = null;
let lastCheckInterval = null;


/* =========================================================
   COPY IP BUTTON
   ========================================================= */

function setupCopyButton() {

    const copyButton =
        document.querySelector(
            ".copy-button"
        );


    if (!copyButton) {
        return;
    }


    if (
        copyButton.dataset.copySetup ===
        "true"
    ) {
        return;
    }


    copyButton.dataset.copySetup =
        "true";


    copyButton.addEventListener(
        "click",
        async () => {

            try {

                await navigator.clipboard.writeText(
                    websiteSettings.serverIP
                );


                copyButton.textContent =
                    "Copied!";


                setTimeout(() => {

                    copyButton.textContent =
                        "Copy IP";

                }, 2000);

            }

            catch (error) {

                console.error(
                    "Could not copy server IP:",
                    error
                );

            }

        }
    );

}


/* =========================================================
   MOBILE MENU
   ========================================================= */

function setupMenu() {

    const menuButton =
        document.querySelector(
            ".menu-button"
        );


    const navLinks =
        document.querySelector(
            ".nav-links"
        );


    if (
        !menuButton ||
        !navLinks
    ) {
        return;
    }


    if (
        menuButton.dataset.menuSetup ===
        "true"
    ) {
        return;
    }


    menuButton.dataset.menuSetup =
        "true";


    menuButton.addEventListener(
        "click",
        (event) => {

            event.preventDefault();


            navLinks.classList.toggle(
                "active"
            );

        }
    );

}


/* =========================================================
   DROPDOWNS
   ========================================================= */

function setupDropdowns() {

    const suggestionButton =
        document.querySelector(
            ".suggestion-arrow"
        );


    const suggestionBox =
        document.querySelector(
            ".suggestion-box"
        );


    const statusButton =
        document.querySelector(
            ".status-arrow"
        );


    const statusBox =
        document.querySelector(
            ".status-box"
        );


    console.log(
        "Dropdown setup:",
        suggestionButton,
        suggestionBox,
        statusButton,
        statusBox
    );


    /* -----------------------------------------------------
       SUGGESTIONS DROPDOWN
       ----------------------------------------------------- */

    if (
        suggestionButton &&
        suggestionBox &&
        suggestionButton.dataset.dropdownSetup !==
            "true"
    ) {

        suggestionButton.dataset.dropdownSetup =
            "true";


        suggestionButton.addEventListener(
            "click",
            (event) => {

                event.preventDefault();


                suggestionBox.classList.toggle(
                    "open"
                );

            }
        );

    }


    /* -----------------------------------------------------
       STATUS DROPDOWN
       ----------------------------------------------------- */

    if (
        statusButton &&
        statusBox &&
        statusButton.dataset.dropdownSetup !==
            "true"
    ) {

        statusButton.dataset.dropdownSetup =
            "true";


        statusButton.addEventListener(
            "click",
            (event) => {

                event.preventDefault();


                statusBox.classList.toggle(
                    "open"
                );

            }
        );

    }

}


/* =========================================================
   SERVER STATUS
   ========================================================= */

async function checkServerStatus() {

    const status =
        document.getElementById(
            "server-status"
        );


    const players =
        document.getElementById(
            "player-count"
        );


    const lastChecked =
        document.getElementById(
            "last-checked"
        );


    if (
        !status ||
        !players
    ) {
        return;
    }


    try {

        const response =
            await fetch(
                "https://api.mcstatus.io/v2/status/java/"
                +
                encodeURIComponent(
                    websiteSettings.serverIP
                )
            );


        if (!response.ok) {

            throw new Error(
                "MCStatus API returned "
                +
                response.status
            );

        }


        const data =
            await response.json();


        if (data.online) {

            status.textContent =
                "🟢 Online";


            players.textContent =
                "Players: "
                +
                data.players.online
                +
                "/"
                +
                data.players.max;

        }

        else {

            status.textContent =
                "🔴 Offline";


            players.textContent =
                "Players: 0";

        }

    }

    catch (error) {

        console.error(
            "Server status check failed:",
            error
        );


        status.textContent =
            "⚠️ Error";


        players.textContent =
            "Could not check server";

    }


    lastCheckTime =
        Date.now();


    if (lastChecked) {

        lastChecked.textContent =
            "Last Checked: 0 seconds ago";

    }


    if (!lastCheckInterval) {

        lastCheckInterval =
            setInterval(
                () => {

                    if (
                        lastChecked &&
                        lastCheckTime
                    ) {

                        const seconds =
                            Math.floor(
                                (
                                    Date.now()
                                    -
                                    lastCheckTime
                                )
                                /
                                1000
                            );


                        lastChecked.textContent =
                            "Last Checked: "
                            +
                            seconds
                            +
                            " seconds ago";

                    }

                },
                1000
            );

    }

}


/* =========================================================
   LOADING SCREEN
   ========================================================= */

function setupLoadingScreen() {

    const loadingScreen =
        document.getElementById(
            "loading-screen"
        );


    const loadingPercent =
        document.getElementById(
            "loading-percent"
        );


    const loadingBar =
        document.querySelector(
            ".loading-progress"
        );


    if (!loadingScreen) {
        return;
    }


    if (
        loadingScreen.dataset.loadingSetup ===
        "true"
    ) {
        return;
    }


    loadingScreen.dataset.loadingSetup =
        "true";


    let percent = 0;


    const timer =
        setInterval(
            () => {

                percent++;


                if (loadingPercent) {

                    loadingPercent.textContent =
                        percent + "%";

                }


                if (loadingBar) {

                    loadingBar.style.width =
                        percent + "%";

                }


                if (percent >= 100) {

                    clearInterval(
                        timer
                    );


                    loadingScreen.classList.add(
                        "hide"
                    );

                }

            },
            40
        );

}


/* =========================================================
   SHORTCUTS
   GitHub Pages + Astro Compatible
   ========================================================= */

function setupShortcuts() {

    if (
        window.eastSMPShortcutsSetup
    ) {
        return;
    }


    window.eastSMPShortcutsSetup =
        true;


    /*
     * Astro automatically provides BASE_URL.
     *
     * With:
     *
     * base: "/Official-East-smp-website"
     *
     * BASE_URL becomes:
     *
     * /Official-East-smp-website/
     */

    const base =
        import.meta.env.BASE_URL;


    /* -----------------------------------------------------
       CTRL + SHIFT + B
       -----------------------------------------------------
       Opens:
       /Official-East-smp-website/beta-tester-bot/
       ----------------------------------------------------- */

    document.addEventListener(
        "keydown",
        (event) => {

            if (
                event.ctrlKey &&
                event.shiftKey &&
                event.key.toLowerCase() === "b"
            ) {

                event.preventDefault();


                window.location.href =
                    base +
                    "beta-tester-bot/";

            }


            /* -------------------------------------------------
               CTRL + B

               Opens the beta-tester-bot page.

               This is intentionally the same destination
               as the CTRL + SHIFT + B shortcut for now.
               ------------------------------------------------- */

            if (
                event.ctrlKey &&
                !event.shiftKey &&
                event.key.toLowerCase() === "b"
            ) {

                event.preventDefault();


                window.location.href =
                    base +
                    "beta-tester-bot/";

            }

        }
    );

}


/* =========================================================
   RULE SEARCH
   ========================================================= */

function setupRuleSearch() {

    const search =
        document.getElementById(
            "rule-search"
        );


    const ruleBoxes =
        document.querySelectorAll(
            ".rule-box"
        );


    if (
        !search ||
        ruleBoxes.length === 0
    ) {
        return;
    }


    if (
        search.dataset.searchSetup ===
        "true"
    ) {
        return;
    }


    search.dataset.searchSetup =
        "true";


    search.addEventListener(
        "input",
        () => {

            const value =
                search.value
                    .toLowerCase()
                    .trim();


            ruleBoxes.forEach(
                (box) => {

                    const text =
                        box.textContent
                            .toLowerCase();


                    if (
                        text.includes(value)
                    ) {

                        box.style.display =
                            "block";

                    }

                    else {

                        box.style.display =
                            "none";

                    }

                }
            );

        }
    );

}


/* =========================================================
   LOAD EVERYTHING
   ========================================================= */

function loadEastSMP() {

    console.log(
        "🚀 Loading East SMP features"
    );


    setupCopyButton();

    setupMenu();

    setupDropdowns();

    setupLoadingScreen();

    setupShortcuts();

    setupRuleSearch();

    checkServerStatus();


    console.log(
        "✅ East SMP features loaded"
    );

}


/* =========================================================
   START EAST SMP
   ========================================================= */

function startEastSMP() {

    console.log(
        "🚀 Starting East SMP"
    );


    loadEastSMP();

}


/* =========================================================
   INITIAL PAGE LOAD
   ========================================================= */

if (
    typeof window !== "undefined"
) {

    if (
        document.readyState ===
        "loading"
    ) {

        document.addEventListener(
            "DOMContentLoaded",
            startEastSMP,
            {
                once: true
            }
        );

    }

    else {

        startEastSMP();

    }


    /* -----------------------------------------------------
       Astro client-side navigation
       ----------------------------------------------------- */

    document.addEventListener(
        "astro:page-load",
        startEastSMP
    );

}
```
