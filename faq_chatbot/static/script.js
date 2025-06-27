const textarea = document.getElementById("question");

textarea.addEventListener("keydown", function(event) {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        askQuestion();
    }
});

async function askQuestion() {
    const q = document.getElementById("question").value;
    if (!q.trim()) return;

    document.getElementById("results").innerHTML = "<p>Loading...</p>";

    const response = await fetch("/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q })
    });

    const data = await response.json();
    const container = document.getElementById("results");
    container.innerHTML = "";

    if (data.length === 0) {
        container.innerHTML = "<p>No related entries found.</p>";
        return;
    }

    data.forEach((item, index) => {
        const div = document.createElement("div");
        div.className = "entry";
        div.innerHTML = `
            <div><strong>Match #${index + 1} (Similarity: ${item.similarity})</strong></div>
            <div class="problem">Problem: ${item.problem}</div>
            <div class="solution"><strong>Answer:</strong> ${item.solution_rephrased}</div>
        `;
        container.appendChild(div);
    });
}
