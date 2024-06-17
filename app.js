const createError = require("http-errors");
const express = require("express");
const path = require("path");
const cookieParser = require("cookie-parser");
const logger = require("morgan");
const { MongoClient } = require("mongodb");
const fs = require("fs");
const { promisify } = require("util");

const writeFileAsync = promisify(fs.writeFile);

const app = express();
const port = process.env.PORT || 3000;

// Middleware
app.use(logger("dev"));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());

// MongoDB Setup
const url = "mongodb://mongo:27017";
const client = new MongoClient(url, { useUnifiedTopology: true });
const dbName = "satellitenbilder";
const collectionName = "data";

// View engine setup (Pug)
app.set("views", path.join(__dirname, "views"));
app.set("view engine", "pug");

// Serve static files from the "public" directory
app.use(express.static(path.join(__dirname, "public")));

// Routes
const indexRouter = require("./routes/index");
app.use("/", indexRouter);

// Route zum Erstellen eines TIF
// TODO In Python Code umwandeln
/** 
app.post("/createTif", async (req, res, next) => {
    try {
        const { latitude, longitude, startYear, endYear } = req.body;

        // Beispiel für die Erstellung eines TIF mit Earth Engine
        const image = ee.ImageCollection('LANDSAT/LC08/C01/T1_TOA')
            .filterBounds(ee.Geometry.Point(parseFloat(longitude), parseFloat(latitude)))
            .filterDate(startYear, endYear)
            .median();

        const tifUrl = await image.getDownloadURL({
            name: 'landsat_image',
            scale: 30,
            region: ee.Geometry.Point(parseFloat(longitude), parseFloat(latitude)).buffer(10000).bounds(),
            filePerBand: false,
            format: 'geotiff',
        });

        const response = await fetch(tifUrl);
        const tifBuffer = await response.buffer();

        const outputPath = path.join(__dirname, 'public', 'tifs', 'landsat_image.tif');
        await writeFileAsync(outputPath, tifBuffer);

        res.send(`TIF wurde erfolgreich erstellt und unter ${outputPath} gespeichert.`);
    } catch (error) {
        console.error('Fehler beim Erstellen des TIF:', error);
        res.status(500).send('Fehler beim Erstellen des TIF');
    }
});
*/
// Catch 404 and forward to error handler
app.use(function(req, res, next) {
    next(createError(404));
});

// Error handler
app.use(function(err, req, res, next) {
    res.locals.message = err.message;
    res.locals.error = req.app.get("env") === "development" ? err : {};

    // Render the error page
    res.status(err.status || 500);
    res.render("error");
});

// Start the server
app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
});

module.exports = app;
