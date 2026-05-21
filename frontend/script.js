function formatTopK(topK = []) {
  return topK.map(c => `${c.name} (${c.score})`).join(" • ");
}

function confidenceBadge(confidence, status) {
  const pct = Math.round(confidence * 100);
  const cls = status === "ok" ? "ok" : "uncertain";
  return `<span class="${cls}">${pct}%</span>`;
}

async function uploadImage() {
  const fileInput = document.getElementById("upload");
  const file = fileInput.files[0];
  const resultsEl = document.getElementById("results");

  if (!file) {
    resultsEl.innerHTML = "<div>Please choose an image first.</div>";
    return;
  }

  const formData = new FormData();
  formData.append("image", file);

  const res = await fetch("http://localhost:5000/scan", {
    method: "POST",
    body: formData
  });

  const data = await res.json();

  if (!res.ok) {
    resultsEl.innerHTML = `<div>Error: ${data.error || "Unknown error"}</div>`;
    return;
  }

  resultsEl.innerHTML = data.results.map(r => `
    <div>
      <strong>Slot ${r.slot}</strong>: ${r.pokemon}
      ${confidenceBadge(r.confidence, r.status)}
      <div>Alternatives: ${formatTopK(r.top_k)}</div>
    </div>
  `).join("");
}
