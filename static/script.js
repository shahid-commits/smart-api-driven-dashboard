// Smart API-Driven Dashboard — main script

// runs only after all HTML elements are loaded
document.addEventListener("DOMContentLoaded", function() {
    
    console.log("Dashboard loaded successfully");

});

// called when user clicks the Ask AI button
async function askAI() {
    
    // grab what the user typed in the AI input box
    const question = document.getElementById("ai-question").value;

    // grab the current city from the hidden input inside the search form
    const city = document.querySelector("input[name='city']").value;

    // don't send empty questions
    if (!question.trim()) {
        alert("Please type a question first!");
        return;
    }
    
    // get the answer box and show a loading message while waiting
    const answerBox = document.getElementById("ai-answer");
    answerBox.style.display = "block";
    answerBox.textContent = "🤖 Thinking...";

    try {
        // send POST request to /ask with city and question as JSON
        const response = await fetch("/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ city: city, question: question })
        });

        // parse the JSON response from FastAPI
        const data = await response.json();

        // display the AI answer in the answer box
        answerBox.textContent = "🤖 " + data.answer;

    } catch (error) {
        // show error message if the request failed
        answerBox.textContent = "❌ Something went wrong. Please try again.";
        console.error("AI request failed:", error);
    }
}