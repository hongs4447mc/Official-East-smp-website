// src/scripts/dropdowns.js

function setupDropdowns() {

	const dropdowns = document.querySelectorAll(".dropdown");


	dropdowns.forEach((dropdown) => {

		const button = dropdown.querySelector(".dropdown-button");


		if (!button) return;


		// Prevent duplicate listeners
		if (button.dataset.dropdownLoaded) return;

		button.dataset.dropdownLoaded = "true";


		button.addEventListener("click", (event) => {

			event.stopPropagation();


			// Close other dropdowns
			dropdowns.forEach((other) => {

				if (other !== dropdown) {
					other.classList.remove("open");
				}

			});


			// Open current dropdown
			dropdown.classList.toggle("open");

		});

	});


}



// Works on first load
document.addEventListener("DOMContentLoaded", setupDropdowns);


// Works with Astro page transitions
document.addEventListener("astro:page-load", setupDropdowns);



// Click outside closes dropdowns
document.addEventListener("click", () => {

	document.querySelectorAll(".dropdown").forEach((dropdown) => {

		dropdown.classList.remove("open");

	});

});



// Escape closes dropdowns
document.addEventListener("keydown", (event) => {

	if (event.key === "Escape") {

		document.querySelectorAll(".dropdown").forEach((dropdown) => {

			dropdown.classList.remove("open");

		});

	}

});