
// =========================================================
// EAST SMP BETA TESTER BOT
// =========================================================

export function setupBetaTesterBot(): void {
	const messagesContainer = document.getElementById("messages");
	const chatInputElement = document.getElementById("chat-input");
	const sendButtonElement = document.getElementById("send-button");
	const statusElement = document.getElementById("status");

	// Make sure all required elements exist and have the
	// correct HTML element types.
	if (!(messagesContainer instanceof HTMLElement)) {
		console.error("Beta Tester Bot: #messages was not found.");
		return;
	}

	if (!(chatInputElement instanceof HTMLInputElement)) {
		console.error("Beta Tester Bot: #chat-input was not found.");
		return;
	}

	if (!(sendButtonElement instanceof HTMLButtonElement)) {
		console.error("Beta Tester Bot: #send-button was not found.");
		return;
	}

	if (!(statusElement instanceof HTMLElement)) {
		console.error("Beta Tester Bot: #status was not found.");
		return;
	}

	const messages = messagesContainer;
	const input = chatInputElement;
	const sendButton = sendButtonElement;
	const status = statusElement;

	// ---------------------------------------------------------
	// ADD MESSAGE
	// ---------------------------------------------------------

	function addMessage(
		text: string,
		type: "bot" | "user"
	): void {
		const messageElement = document.createElement("div");

		messageElement.className = `message ${type}`;
		messageElement.textContent = text;

		messages.appendChild(messageElement);
		messages.scrollTop = messages.scrollHeight;
	}

	// ---------------------------------------------------------
	// BOT RESPONSE
	// ---------------------------------------------------------

	function getBotResponse(userMessage: string): string {
		const message = userMessage.toLowerCase().trim();

		if (!message) {
			return "Please type a message first.";
		}

		if (
			message.includes("hello") ||
			message.includes("hi") ||
			message.includes("hey")
		) {
			return "Hello! I'm the East SMP Beta Tester Bot. What would you like to test?";
		}

		if (
			message.includes("east smp") ||
			message.includes("server")
		) {
			return "East SMP server testing is active. You can test website features, server information, navigation, and the beta system.";
		}

		if (
			message.includes("bug") ||
			message.includes("error") ||
			message.includes("broken") ||
			message.includes("problem")
		) {
			return "Please describe exactly what happened, what you expected to happen, and any error message you saw.";
		}

		if (
			message.includes("test") ||
			message.includes("testing")
		) {
			return "Test received! Try testing navigation, buttons, server status, mobile layout, and the AI response system.";
		}

		if (message.includes("help")) {
			return "I can help test the East SMP website. Try asking about a bug, the server, navigation, or another website feature.";
		}

		if (
			message.includes("status") ||
			message.includes("online")
		) {
			return "You can test the server-status section on the East SMP website to see whether the server is online and how many players are connected.";
		}

		if (
			message.includes("navigation") ||
			message.includes("menu")
		) {
			return "Try opening every navigation link and make sure each page loads correctly. Also test the mobile menu if you are on a small screen.";
		}

		if (
			message.includes("button") ||
			message.includes("buttons")
		) {
			return "Try every button on the website. Make sure buttons respond when clicked and that nothing moves or breaks unexpectedly.";
		}

		return "I received your message. The beta bot is currently using the local test-response system.";
	}

	// ---------------------------------------------------------
	// SEND MESSAGE
	// ---------------------------------------------------------

	function sendMessage(): void {
		const text = input.value.trim();

		if (!text) {
			status.textContent = "Please enter a message.";
			status.className = "status error";
			return;
		}

		addMessage(text, "user");

		input.value = "";

		status.textContent = "Testing response...";
		status.className = "status";

		sendButton.disabled = true;

		// Small delay so the beta tester can see that the bot
		// is processing the request.
		window.setTimeout(() => {
			const response = getBotResponse(text);

			addMessage(response, "bot");

			status.textContent =
				"Response generated successfully.";

			status.className = "status success";

			sendButton.disabled = false;

			input.focus();
		}, 500);
	}

	// ---------------------------------------------------------
	// BUTTON CLICK
	// ---------------------------------------------------------

	sendButton.addEventListener("click", sendMessage);

	// ---------------------------------------------------------
	// ENTER KEY
	// ---------------------------------------------------------

	input.addEventListener(
		"keydown",
		(event: KeyboardEvent) => {
			if (event.key === "Enter") {
				event.preventDefault();
				sendMessage();
			}
		}
	);

	console.log("✅ East SMP Beta Tester Bot loaded");
}

// ---------------------------------------------------------
// START
// ---------------------------------------------------------

if (typeof window !== "undefined") {
	if (document.readyState === "loading") {
		document.addEventListener(
			"DOMContentLoaded",
			setupBetaTesterBot,
			{ once: true }
		);
	} else {
		setupBetaTesterBot();
	}
}

