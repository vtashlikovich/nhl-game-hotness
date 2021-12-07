var dataLoaded = false;
var dataInProgress = false;
var curDay = -1;
var daysBackCheck = 3;
var curTry = 0;
var maxTries = 100;

function processGamesList(data) {
    dataInProgress = false;
    if (data) {
        $('#spinner').hide('fast');

        var lastDate = "";
        for (index in data) {
        var item = data[index];
        var hotnessPic = "";

        if (item.hottness == "HOT") hotnessPic = "hot.png";
        else if (item.hottness == "WOW!") hotnessPic = "wow.png";
        if (hotnessPic.length > 0) hotnessPic = "<img src=\"i/" + hotnessPic + "\">";

        var gameDate = new Date(parseInt(item.date.substring(0, 4)),
            parseInt(item.date.substring(5, 7)) - 1,
            parseInt(item.date.substring(8, 10)));
        gameDate = gameDate.toLocaleDateString('en-us', { day: 'numeric', month:"short", year:"numeric"})
        var date2Show = lastDate != gameDate?gameDate:"";
        lastDate = gameDate;
        var gameYoutubeSrch = item.awayteam + ' vs ' + item.hometeam + ' ' + gameDate;
        var link = "https://www.youtube.com/results?search_query=" + encodeURI(gameYoutubeSrch);

        $('#area').append("<div class=\"row\"><div class=\"col-12 col-md-2 col-xxl-1 date\">" +
            date2Show + "</div><div class=\"col-6 col-md-3 col-xl-2 icons\"><img src=\"teams/" +
            item.awayabr.toUpperCase() + ".png\"><img class=\"div\" src=\"i/div.png\"><img src=\"teams/" + 
            item.homeabr.toUpperCase() + ".png\"></div><div class=\"d-none d-md-block col-md-4 col-lg-3 col-xl-4 col-xxl-5 gametitle\">" +
            "<div class=\"inner\"><span>" + item.awayteam +
            "</span><span>" + item.hometeam + "</span></div></div><div class=\"col-2 col-md-1 col-lg-2 points\">" +
            "<div class=\"inner\"><b>" + item.points + "</b><span>point(s)</span></div></div>" +
            "<div class=\"col-2 col-md-1 hotness\">" + hotnessPic + "</div>" + 
            "<div class=\"col-2 col-md-1 video\"><a href=\"" + link + "\" target=\"_blank\"><img src=\"i/you.png\"></a></div></div>");
        }

        dataLoaded = true;
    }
}

function formFilename(curDay) {
    var curDate = new Date();
    curDate.setDate(curDate.getDate() - curDay);

    console.log(curDate);

    var month = curDate.getMonth() + 1;
    return curDate.getFullYear() + "-" + (month < 10?"0":"") + month + "-" + (curDate.getDate() < 10?"0":"") + curDate.getDate() + ".json";
}

function loadDayData() {
    curTry++;
    if (dataLoaded || curTry > maxTries) return false;
    if (dataInProgress)
    {
        setTimeout(loadDayData, 200);
        return false;
    }

    curDay++;

    if (curDay < daysBackCheck) {
        try {
            dataInProgress = true;
            fetch('log/' + formFilename(curDay))
            .then(response => {
                return response.ok?response.json():null;
            })
            .then(data => processGamesList(data))
            .catch(error => {
                dataInProgress = false;
                console.log('exc:', error);
            });
        }
        catch(exc) {
            console.log('err:' + exc);
        }

        setTimeout(loadDayData, 200);
    }
}