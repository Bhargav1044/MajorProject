async function send() {
  const file = document.getElementById("audio").files[0];
  const fd = new FormData();
  fd.append("audio", file);

  const res = await fetch("/upload", {
    method: "POST",
    body: fd,
  });

  const data = await res.json();
  document.getElementById("out").innerText =
    data.marathi || data.error;
}
