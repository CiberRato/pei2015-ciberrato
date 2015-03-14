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
        $scope.increments = 1;
        $scope.velButton = '1x';

        /* JSON to Object */
        var lab_obj = angular.fromJson(lab);
        var grid_obj = angular.fromJson(grid);
        var parameters_obj = angular.fromJson(parameters);
        var logInfo_obj = angular.fromJson(logInfo);

        var b = 0;

        $scope.slow = 0;
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

        /* Number of Robots */
        $scope.numRobots = $scope.log[0].Robot.length;

        /* Retrieve spawning direction for every robot */
        $scope.dir = [];
        for(i=0; i<$scope.numRobots; i++){
            $scope.dir[i] = parseInt($scope.log[0].Robot[i].Pos._Dir) + 90;
        }

        /* Robots Object */
        $scope.robot = $scope.log[0].Robot;

        /* Time Value */
        $scope.time = $scope.log[0]._Time;

        /* Refresh rate value for each iteration */
        $scope.refresh_rate = $scope.param._CycleTime;

        $scope.idx = 1;
        $scope.last_idx = 0;

        /* Set Robots Colors */
        $scope.mickeyColor = ['img/svg/mickey_red_smile.svg','img/svg/mickey_green_smile.svg','img/svg/mickey_blue_smile.svg','img/svg/mickey_yellow_smile.svg','img/svg/mickey_orange_smile.svg'];

        /* Set Line Colors */
        $scope.lColor = ['#E04F5F','#5FBF60','#29BAF7','#eaea3d','#f28d14'];

        /* Set Maze Colors */
        $scope.groundColor = 'black';
        $scope.cheeseColor = 'img/svg/cheese.svg';
        $scope.circleBorder = '#00ffff';
        $scope.greatWallColor = '#008000';
        $scope.smallWallColor = '#0000ff';
        $scope.gridColor = '#cfd4db';

        /* Line points */
        $scope.pline = [];

        /* Line Toggled */
        $scope.slyne = [];

        /* Line Button Text */
        $scope.toggleText = [];

        /* Line Button Class */
        $scope.bclass = [];

        /* Robot Color */
        $scope.robotColor = [];

        /* Line Color */
        $scope.lineColor = [];
        
        for(i=0; i<$scope.numRobots; i++){
            $scope.pline[i] = "";
            $scope.bclass[i] = 'btn btn-success'
            $scope.toggleText[i] = 'Show';
            $scope.slyne[i] = false;
            if (i>4){
                $scope.robotColor[i] = $scope.mickeyColor[0];
                $scope.lineColor[i] = $scope.lColor[0];
            }
            else{
                $scope.robotColor[i] = $scope.mickeyColor[i];
                $scope.lineColor[i] = $scope.lColor[i];
            }
        }

        $scope.activeV = function(str) {
            if (str=='1x'){
                $scope.velButton = '1x';
                $scope.refresh_rate=50;
                $scope.slow=0;
            }else if (str=='2x'){
                $scope.velButton = '2x';
                $scope.refresh_rate=25;
                $scope.slow=0;
            }else if (str=='4x'){
                $scope.velButton = '4x';
                $scope.refresh_rate=12.5;
                $scope.slow=0;
            }else if (str=='18x'){
                $scope.velButton = '18x';
                $scope.refresh_rate=400;
                $scope.slow=1;
            }else if (str=='14x'){
                $scope.velButton = '14x';
                $scope.refresh_rate=100;
                $scope.slow=0;
            }
        }

        $scope.toggle = function(index) {
            $scope.toggleText[index] = $scope.slyne[index] ? 'Show' : 'Hide';
            if ($scope.bclass[index] === 'btn btn-success')
                $scope.bclass[index] = 'btn btn-danger';
            else
                $scope.bclass[index] = 'btn btn-success';
            $scope.slyne[index] = !$scope.slyne[index];  
        };

        
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
            console.log($scope.radioModel);
            $scope.robot = $scope.log[$scope.idx].Robot;
            $scope.time = $scope.log[$scope.idx]._Time;

            /* Update directions of every robot */
            for(i=0; i<$scope.numRobots; i++){
                $scope.dir[i] = parseInt($scope.log[$scope.idx].Robot[i].Pos._Dir) + 90;
            }
            /* Calculate visited points line */
            if(($scope.last_idx+1)!=$scope.idx){

                for(i=0; i<$scope.numRobots; i++){
                    $scope.pline[i] = "";
                }
                for(b=0;b<$scope.idx;b++){

                    for(i=0; i<$scope.numRobots; i++){
                        $scope.pline[i] += $scope.log[b].Robot[i].Pos._X*$scope.zoom + "," + $scope.log[b].Robot[i].Pos._Y*$scope.zoom + " ";
                    }
                }
            }else {
                for(i=0; i<$scope.numRobots; i++){
                    $scope.pline[i] += $scope.log[$scope.idx].Robot[i].Pos._X * $scope.zoom + "," + $scope.log[$scope.idx].Robot[i].Pos._Y * $scope.zoom + " ";
                }
            }
            $scope.last_idx = $scope.idx;

        }

        $scope.refreshSVG = function(){
            $scope.updateValues();
            $timeout($scope.refreshSVG, 1000);

        }

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
        $scope.setIncrements = function(id){

            if(id == 1){
                $scope.increments = 1;
            }
            if(id == 2){
                $scope.increments = 10;
            }
            if(id == 3){
                $scope.increments = 100;
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

    .directive('conversation', function() {
        return {
            restrict: 'E',
            replace: true,
            compile: function(tElement, attr) {
                attr.$observe('typeId', function(data) {
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
