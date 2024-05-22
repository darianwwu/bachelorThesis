var express = require('express');
var router = express.Router();

/* GET home page. */
router.get('/', function(req, res, next) {
  res.render('index', { title: 'Citizen Science - Lärmkartierung Münster' });
});

module.exports = router;