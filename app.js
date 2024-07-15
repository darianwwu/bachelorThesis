const createError = require("http-errors");
const express = require("express");
const cors = require('cors');
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
app.use(cors());
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
