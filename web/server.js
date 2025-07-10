const express = require("express");
const path = require("path");
const fs = require("fs");

const app = express();
const PORT = 4000;
const OUTPUT_DIR = path.join(__dirname, "output");

// Serve static files
app.use("/output", express.static(OUTPUT_DIR));

app.get("/", (req, res) => {
    let links = [];

    // Traverse the output directory
    fs.readdirSync(OUTPUT_DIR).forEach(dateDir => {
        const datePath = path.join(OUTPUT_DIR, dateDir);
        if (fs.statSync(datePath).isDirectory()) {
            fs.readdirSync(datePath).forEach(urlDir => {
                const filePath = path.join(datePath, urlDir, "index.html");
                if (fs.existsSync(filePath)) {
                    const relPath = path.relative(__dirname, filePath);
                    links.push({
                        label: `${dateDir}/${urlDir}`,
                        href: `/output/${dateDir}/${urlDir}/index.html`
                    });
                }
            });
        }
    });

    // Render basic HTML
    const html = `
    <!DOCTYPE html>
    <html>
    <head>
        <title>Index List</title>
        <meta charset="UTF-8" />
        <style>
            body { font-family: sans-serif; padding: 2em; }
            a { display: block; margin: 0.5em 0; color: blue; }
        </style>
    </head>
    <body>
        <h1>Available Snapshots</h1>
        ${links.map(link => `<a href="${link.href}" target="_blank">${link.label}</a>`).join("\n")}
    </body>
    </html>
    `;
    res.send(html);
});

app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});
