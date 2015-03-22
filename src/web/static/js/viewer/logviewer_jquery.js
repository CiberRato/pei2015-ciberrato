$(document ).ready(function() {
    $("#play").click(function() {
        $(this).attr("disabled", true);
        $("#pause").removeAttr("disabled");
        $("#stop").removeAttr("disabled");
        return false;
    });
    $("#pause").click(function() {
        $(this).attr("disabled", true);
        $("#play").removeAttr("disabled");
        $("#stop").removeAttr("disabled");
        return false;
    });
    $("#stop").click(function() {
        angular.element('[ng-controller=ctrl]').scope().stop();
        $(this).attr("disabled", true);
        $("#pause").attr("disabled", true);
        $("#play").removeAttr("disabled");
        return false;
    });
    $(window).keypress(function(e) {
        if (e.keyCode == 32 && angular.element('[ng-controller=ctrl]').scope().playvar==1) {
            angular.element('[ng-controller=ctrl]').scope().pause();
            $("#pause").attr("disabled", true);
            $("#play").removeAttr("disabled");
            $("#stop").removeAttr("disabled");
            return false;
        }
        else if (e.keyCode == 32 && angular.element('[ng-controller=ctrl]').scope().playvar==0) {
            angular.element('[ng-controller=ctrl]').scope().play();
            $("#play").attr("disabled", true);
            $("#pause").removeAttr("disabled");
            $("#stop").removeAttr("disabled");
            return false;
        }
    });
    $(document).keydown(function(e) {
        switch(e.which) {
            case 37: // left
                angular.element('[ng-controller=ctrl]').scope().idx-=angular.element('[ng-controller=ctrl]').scope().increments;
                break;

            case 38: // up
                break;

            case 39: // right
                angular.element('[ng-controller=ctrl]').scope().idx+=angular.element('[ng-controller=ctrl]').scope().increments;
                break;

            case 40: // down
                break;

            default: return; // exit this handler for other keys
        }
        e.preventDefault(); // prevent the default action (scroll / move caret)
    });
    $("#mazeColor").change(function() {
        angular.element('[ng-controller=ctrl]').scope().setMazeColor($( "#mazeColor" ).val());
        return false;
    });
    $("#increments").change(function() {
        angular.element('[ng-controller=ctrl]').scope().setIncrements($("#increments").val());
        return false;
    });
});