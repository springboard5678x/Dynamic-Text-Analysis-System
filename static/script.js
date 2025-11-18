const reviewInput = document.getElementById("reviewInput");
const analyzeBtn = document.getElementById("analyzeBtn");
const clearBtn = document.getElementById("clearBtn");
const fileInput = document.getElementById("fileInput");

const loadingMsg = document.getElementById("loadingMsg");
const errorMsg = document.getElementById("errorMsg");

const resultsSection = document.getElementById("resultsSection");

const sentimentLabel = document.getElementById("sentimentLabel");
const sentimentProb = document.getElementById("sentimentProb");

const extractiveSummary = document.getElementById("extractiveSummary");
const abstractiveSummary = document.getElementById("abstractiveSummary");

const insightsList = document.getElementById("insightsList");
const recList = document.getElementById("recList");

const topicChartCanvas = document.getElementById("topicChart");
let topicChart = null;

/* ---------------------------
   File Upload
--------------------------- */
fileInput.addEventListener("change", () => {
    const file = fileInput.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = () => {
        reviewInput.value = reader.result;
    };
    reader.readAsText(file);
});

/* ---------------------------
   Clear Results
--------------------------- */
function clearResults() {
    resultsSection.classList.add("hidden");
    document.getElementById("wordCloud").innerHTML = "";

    if (topicChart) {
        topicChart.destroy();
        topicChart = null;
    }
}

/* ---------------------------
   CLEAR BUTTON
--------------------------- */
clearBtn.addEventListener("click", () => {
    reviewInput.value = "";
    errorMsg.classList.add("hidden");
    loadingMsg.classList.add("hidden");

    clearResults();

    sentimentLabel.textContent = "–";
    sentimentProb.textContent = "";
    extractiveSummary.textContent = "–";
    abstractiveSummary.textContent = "–";
    insightsList.innerHTML = "";
    recList.innerHTML = "";
});

/* ---------------------------
   Analyze Review
--------------------------- */
async function analyze() {
    const text = reviewInput.value.trim();
    if (!text) {
        errorMsg.textContent = "Please enter or upload a review.";
        errorMsg.classList.remove("hidden");
        return;
    }

    clearResults();
    loadingMsg.classList.remove("hidden");

    try {
        const res = await fetch("/api/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text }),
        });

        const data = await res.json();
        loadingMsg.classList.add("hidden");

        if (data.status !== "success") {
            errorMsg.textContent = data.message;
            errorMsg.classList.remove("hidden");
            return;
        }

        resultsSection.classList.remove("hidden");

        // Sentiment
        sentimentLabel.textContent = data.sentiment;
        sentimentProb.textContent =
            `Negative: ${(data.probabilities.Negative * 100).toFixed(1)}% • ` +
            `Neutral: ${(data.probabilities.Neutral * 100).toFixed(1)}% • ` +
            `Positive: ${(data.probabilities.Positive * 100).toFixed(1)}%`;

        // Summaries
        extractiveSummary.textContent = data.extractive_summary;
        abstractiveSummary.textContent = data.abstractive_summary;

        // Insights + Recommendations
        insightsList.innerHTML = data.insights.map(i => `<li>${i}</li>`).join("");
        recList.innerHTML = data.recommendations.map(r => `<li>${r}</li>`).join("");

        // Word Cloud
        const colorPalette = [
            "#ffffff", "#e8e8ff", "#c7d2fe", "#bae6fd", "#e9d5ff", "#f5d0fe"
        ];

        WordCloud(document.getElementById("wordCloud"), {
            list: data.wordcloud.map(w => [w.text, Math.round(w.weight * 35)]),
            backgroundColor: "transparent",
            weightFactor: 2,
            gridSize: 10,
            rotateRatio: 0.1,
            color: () => colorPalette[Math.floor(Math.random() * colorPalette.length)]
        });

        // Topic Chart
        topicChart = new Chart(topicChartCanvas, {
            type: "bar",
            data: {
                labels: data.topics.map(t => t.label),
                datasets: [{
                    label: "Topic Relevance",
                    data: data.topics.map(t => t.score),
                    backgroundColor: "#7a70ff",
                }]
            },
            options: {
                scales: {
                    x: { ticks: { color: "#ccc" }},
                    y: { ticks: { color: "#ccc" }, max: 1 }
                },
                plugins: { legend: { labels: { color: "#fff" }} }
            }
        });

    } catch (err) {
        loadingMsg.classList.add("hidden");
        errorMsg.textContent = "Server error. Please try again.";
        errorMsg.classList.remove("hidden");
    }
}

analyzeBtn.addEventListener("click", analyze);
