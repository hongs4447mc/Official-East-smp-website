/* =========================================================
   EAST SMP — SKIP LOADING SCRIPT
   Astro Compatible

   Shortcut:
   CTRL + ALT + SHIFT + L
========================================================= */


console.log(
    "✅ EAST SMP Skip Loading Script Loaded"
);



/* =========================================================
   SKIP FUNCTION
========================================================= */

function skipLoading() {


    console.log(
        "⏩ EAST SMP Loading Skipped"
    );



    const loadingScreen =
        document.getElementById(
            "loading-screen"
        );


    const loadingBar =
        document.querySelector(
            ".loading-progress"
        );


    const loadingPercent =
        document.getElementById(
            "loading-percent"
        );



    console.log(
        "Loading screen:",
        loadingScreen
    );



    /*
        Stop loading timer
    */

    if (
        loadingScreen &&
        loadingScreen._eastTimer
    ) {


        clearInterval(
            loadingScreen._eastTimer
        );


        loadingScreen._eastTimer =
            null;


    }



    /*
        Complete progress
    */

    if (
        loadingBar
    ) {

        loadingBar.style.width =
            "100%";

    }



    if (
        loadingPercent
    ) {

        loadingPercent.textContent =
            "100%";

    }



    /*
        Hide loader
    */

    if (
        loadingScreen
    ) {


        loadingScreen.classList.add(
            "hide"
        );


        loadingScreen.style.display =
            "none";


    }



    document.body.classList.remove(
        "loading"
    );

}



/* =========================================================
   SHORTCUT SETUP
========================================================= */

function setupSkipShortcut() {


    if (
        window.skipShortcutLoaded
    ) {

        return;

    }


    window.skipShortcutLoaded =
        true;



    document.addEventListener(
        "keydown",
        (event) => {



            console.log(
                "KEY:",
                event.key,
                "CTRL:",
                event.ctrlKey,
                "ALT:",
                event.altKey,
                "SHIFT:",
                event.shiftKey
            );



            /*
                CTRL + ALT + SHIFT + L
            */

            if (

                event.ctrlKey &&

                event.altKey &&

                event.shiftKey 

            ) {


                console.log(
                    "⌨️ Skip shortcut detected"
                );


                event.preventDefault();


                skipLoading();


            }


        }
    );


}



/* =========================================================
   START
========================================================= */

function startSkipLoading() {


    setupSkipShortcut();


    console.log(
        "✅ Skip loading shortcut ready"
    );


}



if (
    typeof window !== "undefined"
) {


    if (
        document.readyState === "loading"
    ) {


        document.addEventListener(
            "DOMContentLoaded",
            startSkipLoading,
            {
                once:true
            }
        );


    }

    else {


        startSkipLoading();


    }



    /*
       Astro navigation
    */

    document.addEventListener(
        "astro:page-load",
        startSkipLoading
    );


}



/* =========================================================
   CONSOLE TEST COMMAND
========================================================= */

window.skipLoading =
    skipLoading;