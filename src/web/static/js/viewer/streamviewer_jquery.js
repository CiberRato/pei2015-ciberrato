$("#play").click(function() {
    angular.element('[ng-controller=StreamViewer]').scope().play();
    $(this).attr("disabled", true);
    $("#pause").removeAttr("disabled");
    $("#stop").removeAttr("disabled");
    return false;
});
$("#pause").click(function() {
    angular.element('[ng-controller=StreamViewer]').scope().pause();
    $(this).attr("disabled", true);
    $("#play").removeAttr("disabled");
    $("#stop").removeAttr("disabled");
    return false;
});
$(window).keypress(function(e) {
    if (e.keyCode == 32 && angular.element('[ng-controller=StreamViewer]').scope().playvar==1) {
        angular.element('[ng-controller=StreamViewer]').scope().pause();
        $("#pause").attr("disabled", true);
        $("#play").removeAttr("disabled");
        return false;
    }
    else if (e.keyCode == 32 && angular.element('[ng-controller=StreamViewer]').scope().playvar==0) {
        angular.element('[ng-controller=StreamViewer]').scope().play();
        $("#play").attr("disabled", true);
        $("#pause").removeAttr("disabled");
        return false;
    }
});
$("#mazeColor").change(function() {
    angular.element('[ng-controller=StreamViewer]').scope().setMazeColor($( "#mazeColor" ).val());
    return false;
});
