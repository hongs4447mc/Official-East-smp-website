/*
=================================
EAST SMP WEBSITE TESTER
ASTRO COMPATIBLE VERSION
=================================
*/


async function runWebsiteTests(progress){

	const results = [];


	function addResult(type,name,passed){

		results.push({

			type,

			name,

			passed:Boolean(passed)

		});

	}



	async function getHomeHTML(){

		try{

			const response = await fetch("/");

			return await response.text();

		}

		catch{

			return "";

		}

	}



	const tests = [

		// KEEP ALL YOUR TESTS HERE
		// Pages
		// Buttons
		// Components
		// Server
		// Performance
		// Security

	];



	let done = 0;



	for(const test of tests){

		let passed = false;


		try{

			passed = await test.run();

		}

		catch{

			passed = false;

		}



		addResult(

			test.type,

			test.name,

			passed

		);



		done++;



		if(progress){

			progress(

				Math.floor(
					(done / tests.length) * 100
				)

			);

		}



		await new Promise(

			resolve => setTimeout(resolve,150)

		);


	}



	addResult(

		"⚙️ Bot",

		"Tester Bot Running",

		true

	);



	return results;

}



/*
=================================
MAKE AVAILABLE TO BROWSER ONLY
=================================
*/


if(typeof window !== "undefined"){

	window.runWebsiteTests = runWebsiteTests;

}