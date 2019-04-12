const express = require("express");
const compress = require('compression');
const ejs = require('ejs');
const path = require('path');
const bodyParser = require('body-parser');
const session = require('express-session');
const cookieParser = require('cookie-parser');
const app = express();

app.use(compress());
app.use(bodyParser.urlencoded({extended: false}));
app.use(bodyParser.json());
app.use(cookieParser());
app.use(express.static(path.join(__dirname, "dist")));

app.get('/', function (req, res, next) {
    res.redirect('/vmManager');
});

app.get('/vmManager(/?*)', function (req, res, next) {
    // const session = req.session;
    // const username = session.username;
    // const isLogined = !!username;
    // const options = {
    //     headers: {
    //         'x-timestamp': Date.now(),
    //         'x-sent': true
    //     }
    // };
    // res.cookie('username',username);
    res.sendFile(path.join(__dirname, "dist", "resource") + '/vmManager/index.html');
});

app.listen(3000, function () {
    console.log("3000");
});