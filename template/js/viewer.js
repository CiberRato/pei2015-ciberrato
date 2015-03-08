function convertToStringPoints(cornerList, zoom){
    var out = "";
    var b = 0;
    for(; b<cornerList.Corner.length; b++){
        out+= cornerList.Corner[b]._X*zoom + "," + cornerList.Corner[b]._Y*zoom + " ";
    }
    return out;
}

angular.module('myapp', [])
    .controller('ctrl', ['$scope', '$timeout', function($scope, $timeout){
        /* Zoom variable (30->Standard) */
        $scope.zoom = 30;

        /* JSON to Object */
        var lab_obj = angular.fromJson(lab);
        var grid_obj = angular.fromJson(grid);
        var parameters_obj = angular.fromJson(parameters);
        var logInfo_obj = angular.fromJson(logInfo);

        var b = 0;
        $scope.playvar = 0;

        /* Convert wall points to be integrated in SVG */
        for(i=0; i<lab_obj.Lab.Wall.length; i++){
            lab_obj.Lab.Wall[i].str = convertToStringPoints(lab_obj.Lab.Wall[i], $scope.zoom);
        }

        /* Parameters Object */
        $scope.param=parameters_obj.Parameters;

        /* Map Object */
        $scope.map = lab_obj.Lab;

        /* Grid Object */
        $scope.grid = grid_obj.Grid;

        /* Log Object */
        $scope.log = logInfo_obj.Log.LogInfo;

        /* Beacons Object */
        $scope.beacon = lab_obj.Lab.Beacon;

        /* Find beacon height */
        if($scope.param._NBeacons == 1)
            $scope.beacon_height = lab_obj.Lab.Beacon._Height;
        else
            $scope.beacon_height = lab_obj.Lab.Beacon[0]._Height;

        /* Retrieve spawning direction for every robot */
        try{
            $scope.dir1= parseInt($scope.log[0].Robot[0].Pos._Dir) + 90;
            $scope.dir2= parseInt($scope.log[0].Robot[1].Pos._Dir) + 90;
            $scope.dir3= parseInt($scope.log[0].Robot[2].Pos._Dir) + 90;
            $scope.dir4= parseInt($scope.log[0].Robot[3].Pos._Dir) + 90;
            $scope.dir5= parseInt($scope.log[0].Robot[4].Pos._Dir) + 90;
        }catch(TypeError){

        }
        /* Robots Object */
        $scope.robot = $scope.log[0].Robot;

        /* Time Value */
        $scope.time = $scope.log[0]._Time;

        /* Refresh rate value for each iteration */
        $scope.refresh_rate = $scope.param._CycleTime;

        $scope.idx = 1;
        $scope.last_idx = 0;

        $scope.pline1 = "";
        $scope.pline2 = "";
        $scope.pline3 = "";
        $scope.pline4 = "";
        $scope.pline5 = "";

        /* Set Robots Colors */
        $scope.robotColor1 = 'img/svg/mickey_red_smile.svg';
        $scope.robotColor2 = 'img/svg/mickey_green_smile.svg';
        $scope.robotColor3 = 'img/svg/mickey_blue_smile.svg';
        $scope.robotColor4 = 'img/svg/mickey_yellow_smile.svg';
        $scope.robotColor5 = 'img/svg/mickey_orange_smile.svg';

        /* Set Maze Colors */
        $scope.groundColor = 'black';
        $scope.cheeseColor = 'img/svg/cheese.svg';
        $scope.circleBorder = '#00ffff';
        $scope.greatWallColor = '#008000';
        $scope.smallWallColor = '#0000ff';
        $scope.gridColor = '#cfd4db';

        var refresh = function(refresh_rate){
            $timeout(tick, refresh_rate);
        }

        /* Update timeline */
        var tick = function() {
            try{
                $scope.updateValues();

                $(".leftGrip").css("left", ($scope.idx*820)/$scope.param._SimTime);
                if($scope.play){
                    $scope.idx++;
                }
            }catch(TypeError){
                $scope.pause();
            }
            if($scope.playvar){
                refresh($scope.refresh_rate);
            }
        };

        /* Update Viewer Values */
        $scope.updateValues = function(){

            $scope.robot = $scope.log[$scope.idx].Robot;
            $scope.time = $scope.log[$scope.idx]._Time;

            /* Update directions of every robot */
            try{
                $scope.dir1= parseInt($scope.log[$scope.idx].Robot[0].Pos._Dir) + 90;
                $scope.dir2= parseInt($scope.log[$scope.idx].Robot[1].Pos._Dir) + 90;
                $scope.dir3= parseInt($scope.log[$scope.idx].Robot[2].Pos._Dir) + 90;
                $scope.dir4= parseInt($scope.log[$scope.idx].Robot[3].Pos._Dir) + 90;
                $scope.dir5= parseInt($scope.log[$scope.idx].Robot[4].Pos._Dir) + 90;
            }catch(TypeError){

            }
            /* Calculate visited points line */
            if(($scope.last_idx+1)!=$scope.idx){

                $scope.pline1 = "";
                $scope.pline2 = "";
                $scope.pline3 = "";
                $scope.pline4 = "";
                $scope.pline5 = "";
                for(b=0;b<$scope.idx;b++){
                    try{
                        $scope.pline1 += $scope.log[b].Robot[0].Pos._X*$scope.zoom + "," + $scope.log[b].Robot[0].Pos._Y*$scope.zoom + " ";
                        $scope.pline2 += $scope.log[b].Robot[1].Pos._X*$scope.zoom + "," + $scope.log[b].Robot[1].Pos._Y*$scope.zoom + " ";
                        $scope.pline3 += $scope.log[b].Robot[2].Pos._X*$scope.zoom + "," + $scope.log[b].Robot[2].Pos._Y*$scope.zoom + " ";
                        $scope.pline4 += $scope.log[b].Robot[3].Pos._X*$scope.zoom + "," + $scope.log[b].Robot[3].Pos._Y*$scope.zoom + " ";
                        $scope.pline5 += $scope.log[b].Robot[4].Pos._X*$scope.zoom + "," + $scope.log[b].Robot[4].Pos._Y*$scope.zoom + " ";
                    }catch(TypeError){

                    }
                }
            }else {
                try {
                    $scope.pline1 += $scope.log[$scope.idx].Robot[0].Pos._X * $scope.zoom + "," + $scope.log[$scope.idx].Robot[0].Pos._Y * $scope.zoom + " ";
                    $scope.pline2 += $scope.log[$scope.idx].Robot[1].Pos._X * $scope.zoom + "," + $scope.log[$scope.idx].Robot[1].Pos._Y * $scope.zoom + " ";
                    $scope.pline3 += $scope.log[$scope.idx].Robot[2].Pos._X * $scope.zoom + "," + $scope.log[$scope.idx].Robot[2].Pos._Y * $scope.zoom + " ";
                    $scope.pline4 += $scope.log[$scope.idx].Robot[3].Pos._X * $scope.zoom + "," + $scope.log[$scope.idx].Robot[3].Pos._Y * $scope.zoom + " ";
                    $scope.pline5 += $scope.log[$scope.idx].Robot[4].Pos._X * $scope.zoom + "," + $scope.log[$scope.idx].Robot[4].Pos._Y * $scope.zoom + " ";
                }catch(TypeError){

                }
            }
            $scope.last_idx = $scope.idx;

        }

        $scope.refreshSVG = function(){
            $scope.updateValues();
            $timeout($scope.refreshSVG, 1000);

        }
        /*$scope.setRobotColor = function(id){

            if(id == 1){
                $scope.robotColor = 'img/svg/mickey_red_smile.svg';
            }
            if(id == 2){
                $scope.robotColor = 'img/svg/mickey_blue_smile.svg';
            }
            if(id == 3){
                $scope.robotColor = 'img/svg/mickey_green_smile.svg';
            }
        };*/

        $scope.setMazeColor = function(id){

            if(id == 1){
                $scope.groundColor = 'black';
                $scope.cheeseColor = 'img/svg/cheese.svg';
                $scope.circleBorder = '#00ffff';
                $scope.greatWallColor = '#008000';
                $scope.smallWallColor = '#0000ff';
                $scope.gridColor = '#cfd4db';

            }
            if(id == 2){
                $scope.groundColor = 'darkgrey';
                $scope.cheeseColor = 'img/svg/blackCheese.svg';
                $scope.circleBorder = '#cfd4db';
                $scope.greatWallColor = '#353535';
                $scope.smallWallColor = '#727272';
                $scope.gridColor = '#cfd4db';

            }

        };

        $scope.play = function() {
            if(!$scope.playvar){
                $scope.playvar = 1;
                refresh($scope.refresh_rate);
            }
        };

        $scope.pause = function(){
            if($scope.playvar){
                $scope.playvar = 0;
                $timeout($scope.refreshSVG, 1000);
            }
        };

        $scope.stop = function(){
            $scope.idx = 0;
            $scope.playvar = 0;
            refresh(0);
        };
    }])

    .directive('ngCx', function() {
        return function(scope, element, attrs) {
            scope.$watch(attrs.ngCx, function(value) {
                element.attr('cx', value);
            });
        };
    })
    .directive('ngCy', function() {
        return function(scope, element, attrs) {
            scope.$watch(attrs.ngCy, function(value) {
                element.attr('cy', value);
            });
        };
    })
    .directive('ngX', function() {
        return function(scope, element, attrs) {
            scope.$watch(attrs.ngX, function(value) {
                element.attr('x', value);
            });
        };
    })
    .directive('ngY', function() {
        return function(scope, element, attrs) {
            scope.$watch(attrs.ngY, function(value) {
                element.attr('y', value);
            });
        };
    })
    .directive('ngR', function() {
        return function(scope, element, attrs) {
            scope.$watch(attrs.ngR, function(value) {
                element.attr('r', value);
            });
        };
    })
    .directive('ngH', function() {
        return function(scope, element, attrs) {
            scope.$watch(attrs.ngH, function(value) {
                element.attr('height', value);
            });
        };
    })
    .directive('ngW', function() {
        return function(scope, element, attrs) {
            scope.$watch(attrs.ngW, function(value) {
                element.attr('width', value);
            });
        };
    })
    .directive('ngT', function() {
        return function(scope, element, attrs) {
            scope.$watch(attrs.ngT, function() {
                console.log(attrs.ngT);
                element.attr('transform', attrs.ngT);
            });
        };
    })
    .directive('ngPoints', function() {
        return function(scope, element, attrs) {
            scope.$watch(attrs.ngPoints, function(value) {
                element.attr('points', value);
            });
        };
    })
    .directive('conversation', function() {
        return {
            restrict: 'E',
            replace: true,
            compile: function(tElement, attr) {
                attr.$observe('typeId', function(data) {
                    console.log("Updated data ", data);
                }, true);

            }
        };
    });


var parameters;
var logInfo;
var grid;
var lab;

angular.element(document).ready(function(){
    $.get( "logs/lab_json.txt", function( data ) {
        lab = data;
        $.get( "logs/parameters_json.txt", function( data ) {
            parameters = data;
            $.get( "logs/grid_json.txt", function( data ) {
                grid = data;
                $.get( "logs/log_json.txt", function( data ) {
                    logInfo = data;

                    angular.bootstrap(document, ['myapp']);

                    $("#waitawhile").hide("fast");
                    $("#row1").show("slow");
                    $("#row2").show("slow");
                    $("#row3").show("slow");
                    $("#row4").show("slow");
                    $("#row5").show("slow");

                    $('.nstSlider').nstSlider({
                        "left_grip_selector": ".leftGrip",
                        "value_changed_callback": function(cause, leftValue, rightValue) {
                            try{
                                var scope = angular.element('[ng-controller=ctrl]').scope();
                                scope.idx = leftValue;

                            }catch(TypeError){}
                        }
                    });

                    // Call methods and such...
                    var highlightMin = Math.random() * 20,
                        highlightMax = highlightMin + Math.random() * 80;
                    $('.nstSlider').nstSlider('highlight_range', highlightMin, highlightMax);
                });
            });
        });
    });
});
