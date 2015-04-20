window.onresize = doALoadOfStuff;

function doALoadOfStuff() {
    if(angular.element('[ng-controller=LogViewer]').scope().load){
        var i;
        angular.element('[ng-controller=LogViewer]').scope().zoom = (document.getElementById("svgrow").offsetWidth *31.5) / 880;
        for (i = 0; i < angular.element('[ng-controller=LogViewer]').scope().map.Wall.length; i++) {
            //console.log(lab_obj);
            angular.element('[ng-controller=LogViewer]').scope().map.Wall[i].str = angular.element('[ng-controller=LogViewer]').scope().convertToStringPoints(angular.element('[ng-controller=LogViewer]').scope().map.Wall[i], angular.element('[ng-controller=LogViewer]').scope().zoom);
        }
        angular.element('[ng-controller=LogViewer]').scope().$apply();

    }
    angular.element('[ng-controller=LogViewer]').scope().load = true;
}

var handler = window.onresize;
handler();

$("#play").click(function() {
    angular.element('[ng-controller=LogViewer]').scope().play();
    console.log("OK");
    $(this).attr("disabled", true);
    $("#pause").removeAttr("disabled");
    $("#stop").removeAttr("disabled");
    return false;
});
$("#pause").click(function() {
    angular.element('[ng-controller=LogViewer]').scope().pause();
    $(this).attr("disabled", true);
    $("#play").removeAttr("disabled");
    $("#stop").removeAttr("disabled");
    return false;
});
$("#stop").click(function() {
    angular.element('[ng-controller=LogViewer]').scope().stop();
    $(this).attr("disabled", true);
    $("#pause").attr("disabled", true);
    $("#play").removeAttr("disabled");
    return false;
});
$(window).keypress(function(e) {
    if (e.keyCode == 32 && angular.element('[ng-controller=LogViewer]').scope().playvar==1) {
        angular.element('[ng-controller=LogViewer]').scope().pause();
        $("#pause").attr("disabled", true);
        $("#play").removeAttr("disabled");
        $("#stop").removeAttr("disabled");
        return false;
    }
    else if (e.keyCode == 32 && angular.element('[ng-controller=LogViewer]').scope().playvar==0) {
        angular.element('[ng-controller=LogViewer]').scope().play();
        $("#play").attr("disabled", true);
        $("#pause").removeAttr("disabled");
        $("#stop").removeAttr("disabled");
        return false;
    }
});
$(document).keydown(function(e) {
    switch(e.which) {
        case 37: // left
            angular.element('[ng-controller=LogViewer]').scope().idx-=angular.element('[ng-controller=LogViewer]').scope().increments;
            break;

        case 38: // up
            break;

        case 39: // right
            angular.element('[ng-controller=LogViewer]').scope().idx+=angular.element('[ng-controller=LogViewer]').scope().increments;
            break;

        case 40: // down
            break;

        default: return; // exit this handler for other keys
    }
    e.preventDefault(); // prevent the default action (scroll / move caret)
});
$("#mazeColor").change(function() {
    angular.element('[ng-controller=LogViewer]').scope().setMazeColor($( "#mazeColor" ).val());
    return false;
});
$("#increments").change(function() {
    angular.element('[ng-controller=LogViewer]').scope().setIncrements($("#increments").val());
    return false;
});
