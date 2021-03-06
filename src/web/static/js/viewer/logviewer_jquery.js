$("#play").click(function() {
    angular.element('[ng-controller=LogViewer]').scope().play();
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
    try{
        if (e.keyCode == 32 && angular.element('[ng-controller=LogViewer]') !== 'undefined' && angular.element('[ng-controller=LogViewer]').scope().playvar==1) {
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
    }catch(Exception){}
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

