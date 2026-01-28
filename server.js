const express = require("express");
const multer = require("multer");
const fs = require("fs");
const fetch = (...args) =>
  import("node-fetch").then(({ default: fetch }) => fetch(...args));
const FormData = require("form-data");

const app = express();
const upload = multer({ dest: "uploads/" });

app.use(express.static("public"));

app.post("/upload", upload.single("audio"), async (req, res) => {
  try {
    const form = new FormData();
    form.append("audio", fs.createReadStream(req.file.path));

    const response = await fetch("http://localhost:5000/api/process-audio", {
      method: "POST",
      body: form,
    });

    const data = await response.json();
    res.json(data);
  } catch (err) {
    res.status(500).json({ error: "Frontend error" });
  }
});

app.listen(3000, () => {
  console.log("Frontend running on http://localhost:3000");
});
