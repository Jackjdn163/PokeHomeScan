async function uploadImage() {
  const fileInput = document.getElementById("upload");
  const file = fileInput.files[0];

  const formData = new FormData();
  formData.append("image", file);

  const res = await fetch("http://localhost:5000/scan", {
    method: "POST",
    body: formData
  });

  const data = await res.json();

  document.getElementById("results").innerHTML =
    data.pokemon.map(p => `<div>${p}</div>`).join("");
}
