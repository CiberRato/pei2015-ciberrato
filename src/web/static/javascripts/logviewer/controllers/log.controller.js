(function(){
    'use strict';

    angular
        .module('ciberonline.logviewer.controllers')
        .controller('LogViewer', LogViewer);

    LogViewer.$inject = ['$location', '$scope', '$routeParams','Round', 'Authentication', 'Profile', 'LogViewer', '$timeout'];

    function LogViewer($location, $scope, $routeParams, Round, Authentication, Profile, LogViewer, $timeout){

        $scope.load=false;

        var c1 = document.getElementById("layer1");
        var ctx1 = c1.getContext("2d");
        var c2 = document.getElementById("layer2");
        var ctx2 = c2.getContext("2d");
        var c3 = document.getElementById("layer4");
        var ctx3 = c3.getContext("2d");

        LogViewer.getLog($routeParams.identifier).then(getLogSuccess, getLogError);

        function getLogSuccess(log){

            $scope.log = log.data.Log;
            $scope.param = log.data.Parameters;
            $scope.map = log.data.Lab;
            $scope.grid = log.data.Grid;

            showViewer();
        }
        function getLogError(){
            console.log("ERROR");
        }
        function showViewer(){

            $("#waitawhile").hide("fast");
            $("#row1").show("slow");
            $("#row3").show("slow");
            $("#row2").show("slow");


            $scope.zoom = 50;

            doIt();
        }

        $scope.drawMap=function(){

            ctx1.clearRect(0, 0, c1.width, c1.height);
            ctx1.rect(0,0, c1.width, c1.height);
            ctx1.fillStyle=$scope.groundColor;
            ctx1.fill();
            drawWalls();
            drawBeacon();
            drawGrid();
        }

        function drawGrid(){
            var i;
            for(i=0;i<$scope.grid.Position.length;i++) {
                ctx1.beginPath();
                ctx1.arc($scope.grid.Position[i]._X*$scope.zoom, $scope.grid.Position[i]._Y*$scope.zoom, $scope.zoom/2, 0, 2 * Math.PI, false);
                ctx1.fillStyle = $scope.gridColor;
                ctx1.fill();
                ctx1.lineWidth = 2;
                ctx1.strokeStyle = $scope.circleBorder;
                ctx1.stroke();
            }
        }

        function drawBeacon(){
            var i;

            for(i=0;i<$scope.map.Beacon.length;i++){
                console.log($scope.map.Beacon[i]);
                ctx1.beginPath();
                ctx1.arc($scope.map.Beacon[i]._X * $scope.zoom, $scope.map.Beacon[i]._Y * $scope.zoom, $scope.zoom * $scope.map.Target[i]._Radius + $scope.zoom/15, 0, 2*Math.PI);
                ctx1.fillStyle = $scope.circleBorder;
                ctx1.fill();

                var dx = ($scope.map.Beacon[i]._X * $scope.zoom) - ($scope.zoom*$scope.map.Target[i]._Radius);
                var dy = ($scope.map.Beacon[i]._Y * $scope.zoom) - ($scope.zoom*$scope.map.Target[i]._Radius);
                var dWidth = $scope.zoom*$scope.map.Target[i]._Radius*2;
                var dHeight = $scope.zoom*$scope.map.Target[i]._Radius*2;

                var imageObj = new Image();
                imageObj.onload = function() {
                    ctx1.drawImage(imageObj, dx, dy, dWidth, dHeight);
                };
                imageObj.src = $scope.cheeseColor;
                ctx1.fill();
                ctx1.stroke();
            }

        }

        function drawWalls(){
            var i;
            for (i = 0; i < $scope.map.Wall.length; i++) {

                if($scope.map.Wall[i]._Height < $scope.map.Beacon[0]._Height){
                    ctx1.fillStyle = $scope.smallWallColor;
                }
                else{
                    ctx1.fillStyle = $scope.greatWallColor;
                }
                ctx1.beginPath();
                var b = 0;
                for(; b < $scope.map.Wall[i].Corner.length; b++){
                    ctx1.lineTo($scope.map.Wall[i].Corner[b]._X * $scope.zoom ,$scope.map.Wall[i].Corner[b]._Y * $scope.zoom);
                }
                ctx1.closePath();
                ctx1.fill();
            }
        }

        $scope.drawLine=function(){
            ctx3.clearRect(0, 0, c3.width, c3.height);
            var i;
            var b;
            for(i = 0; i < $scope.robot.length; i++){
                if($scope.slyne[i]==true){
                    ctx3.beginPath();
                    ctx3.moveTo($scope.plinex[i][0],$scope.pliney[i][0]);
                    for(b = 1; b < $scope.idx; b++){
                        ctx3.lineTo($scope.plinex[i][b],$scope.pliney[i][b]);
                    }
                    ctx3.lineWidth = 5;
                    ctx3.strokeStyle = $scope.lColor[i];
                    ctx3.stroke();
                    console.log('aqui'+b);
                }
            }

        }

        $scope.drawRobots=function(){
            ctx2.clearRect(0, 0, c2.width, c2.height);

            var i;
            var x;
            var y;
            var color;
            var dir;

            for (i = 0; i < $scope.robot.length; i++) {
                ctx2.beginPath();
                ctx2.arc($scope.robot[i].Pos._X * $scope.zoom, $scope.robot[i].Pos._Y * $scope.zoom, $scope.zoom/2, 0, 2 * Math.PI, false);
                ctx2.fillStyle = "rgba(0, 0, 0, 0.0)";
                ctx2.lineWidth = 1;
                ctx2.strokeStyle = $scope.circleBorder;
                ctx2.stroke();
                if($scope.robot[i].Scores._Collision=='True'){
                    x =  $scope.robot[i].Pos._X * $scope.zoom - $scope.zoom/2;
                    y =  $scope.robot[i].Pos._Y * $scope.zoom - $scope.zoom/2;
                    dir = $scope.dir[i];
                    ctx2.save();
                    ctx2.translate(x + $scope.zoom/2,y+ $scope.zoom/2);
                    ctx2.rotate(dir * Math.PI/180);
                    ctx2.drawImage($scope.blackmouse, -$scope.zoom/2, -$scope.zoom/2, $scope.zoom , $scope.zoom );
                    ctx2.fill();
                    ctx2.stroke();
                    ctx2.restore();
                }
                else{
                    x =  $scope.robot[i].Pos._X * $scope.zoom - $scope.zoom/2;
                    y =  $scope.robot[i].Pos._Y * $scope.zoom - $scope.zoom/2;
                    color = $scope.mickeyColor[i];
                    dir = $scope.dir[i];
                    ctx2.save();
                    ctx2.translate(x + $scope.zoom/2,y+ $scope.zoom/2);
                    ctx2.rotate(dir * Math.PI/180);
                    ctx2.drawImage(color, -$scope.zoom/2, -$scope.zoom/2, $scope.zoom , $scope.zoom );
                    ctx2.fill();
                    ctx2.stroke();
                    ctx2.restore();
                }
            }
        }

        function doIt() {

            c1.width=$scope.zoom * $scope.map._Width;
            c1.height=$scope.zoom * $scope.map._Height;
            c2.width=$scope.zoom * $scope.map._Width;
            c2.height=$scope.zoom * $scope.map._Height;
            c3.width=$scope.zoom * $scope.map._Width;
            c3.height=$scope.zoom * $scope.map._Height;
            ctx1.translate(0, $scope.zoom * $scope.map._Height);
            ctx1.scale(1, -1);
            ctx2.translate(0, $scope.zoom * $scope.map._Height);
            ctx2.scale(1, -1);
            ctx3.translate(0, $scope.zoom * $scope.map._Height);
            ctx3.scale(1, -1);

            $scope.velButton = '1x';

            var b = 0;
            var i = 0;

            $scope.slow = 0;
            $scope.playvar = 0;

            /* Number of Beacons */
            $scope.nBeacon = $scope.map.Beacon.length;

            /* Find beacon height */
            $scope.beacon_height = $scope.map.Beacon[0]._Height;

            /* Number of Robots */
            $scope.numRobots = $scope.log[0].LogInfo.Robot.length;


            /* Retrieve spawning direction for every robot */
            $scope.dir = [];
            for (i = 0; i < $scope.numRobots; i++) {
                $scope.dir[i] = parseInt($scope.log[0].LogInfo.Robot[i].Pos._Dir) + 90;
            }

            /* Robots Object */
            $scope.robot = $scope.log[0].LogInfo.Robot;

            /* Time Value */
            $scope.time = $scope.log[0].LogInfo._Time;

            /* Refresh rate value for each iteration */
            $scope.refresh_rate = $scope.param._CycleTime;

            $scope.idx = 1;
            $scope.last_idx = 0;

            $scope.blackmouse = new Image();
            $scope.blackmouse.src = 'static/img/svg/mickey_black_smile.png';
            var redmouse = new Image();
            redmouse.src = 'static/img/svg/mickey_red_smile.png';
            var bluemouse = new Image();
            bluemouse.src = 'static/img/svg/mickey_blue_smile.png';
            var yellowmouse = new Image();
            yellowmouse.src = 'static/img/svg/mickey_yellow_smile.png';
            var orangmouse = new Image();
            orangmouse.src = 'static/img/svg/mickey_orange_smile.png';
            var greenmouse = new Image();
            greenmouse.src = 'static/img/svg/mickey_green_smile.png';

            /* Set Robots Colors */
            $scope.mickeyColor = [redmouse, greenmouse, bluemouse, yellowmouse, orangmouse];
            $scope.mickeys =['static/img/svg/mickey_red_smile.png','static/img/svg/mickey_green_smile.png','static/img/svg/mickey_blue_smile.png','static/img/svg/mickey_yellow_smile.png','static/img/svg/mickey_orange_smile.png'];

            /* Set Line Colors */
            $scope.lColor = ['#E04F5F', '#5FBF60', '#29BAF7', '#eaea3d', '#f28d14'];

            /* Set Maze Colors */
            $scope.groundColor = 'black';
            $scope.cheeseColor = 'static/img/svg/cheese.png';
            $scope.circleBorder = '#00ffff';
            $scope.greatWallColor = '#008000';
            $scope.smallWallColor = '#0000ff';
            $scope.gridColor = '#cfd4db';

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


            $scope.plinex = [];
            $scope.pliney = [];
            for (i = 0; i < $scope.numRobots; i++) {
                $scope.plinex[i] = [];
                $scope.pliney[i] = [];
                $scope.bclass[i] = 'btn btn-success'
                $scope.toggleText[i] = 'Show';
                $scope.slyne[i] = false;
                if (i > 4) {
                    $scope.robotColor[i] = $scope.mickeyColor[0];
                    $scope.lineColor[i] = $scope.lColor[0];
                }
                else {
                    $scope.robotColor[i] = $scope.mickeyColor[i];
                    $scope.lineColor[i] = $scope.lColor[i];
                }
            }

            $scope.drawMap();
            $scope.drawRobots();

            $scope.activeV = function (str) {
                if (str == '1x') {
                    $scope.velButton = '1x';
                    $scope.refresh_rate = 50;
                    $scope.slow = 0;
                } else if (str == '2x') {
                    $scope.velButton = '2x';
                    $scope.refresh_rate = 25;
                    $scope.slow = 0;
                } else if (str == '4x') {
                    $scope.velButton = '4x';
                    $scope.refresh_rate = 12.5;
                    $scope.slow = 0;
                } else if (str == '18x') {
                    $scope.velButton = '18x';
                    $scope.refresh_rate = 400;
                    $scope.slow = 1;
                } else if (str == '14x') {
                    $scope.velButton = '14x';
                    $scope.refresh_rate = 100;
                    $scope.slow = 0;
                }
            }

            $scope.toggle = function (index) {
                $scope.toggleText[index] = $scope.slyne[index] ? 'Show' : 'Hide';
                if ($scope.bclass[index] === 'btn btn-success')
                    $scope.bclass[index] = 'btn btn-danger';
                else
                    $scope.bclass[index] = 'btn btn-success';
                $scope.slyne[index] = !$scope.slyne[index];
            };


            var refresh = function (refresh_rate) {
                $timeout(tick, refresh_rate);
            }

            /* Update timeline */
            var tick = function () {
                try {
                    $scope.updateValues();

                    $(".leftGrip").css("left", ($scope.log[$scope.idx].LogInfo._Time * ($("#tmline").width()-20)) / $scope.param._SimTime);
                    if ($scope.playvar) {
                        $scope.idx++;
                    }
                } catch (TypeError) {
                    $scope.pause();
                }
                if ($scope.playvar) {
                    refresh($scope.refresh_rate);
                }
            };

            /* Update Viewer Values */
            $scope.updateValues = function () {

                $scope.robot = $scope.log[$scope.idx].LogInfo.Robot;
                $scope.time = $scope.log[$scope.idx].LogInfo._Time;

                /* Update directions of every robot */

                for (i = 0; i < $scope.numRobots; i++) {
                    $scope.dir[i] = parseInt($scope.log[$scope.idx].LogInfo.Robot[i].Pos._Dir) + 90;
                }

                /* Calculate visited points line */
                if (($scope.last_idx + 1) != $scope.idx) {

                    for (i = 0; i < $scope.numRobots; i++) {
                        $scope.plinex[i] = [];
                        $scope.pliney[i] = [];
                    }


                    for (b = 0; b < $scope.idx; b++) {

                        for (i = 0; i < $scope.numRobots; i++) {
                            $scope.plinex[i][b] = $scope.log[b].LogInfo.Robot[i].Pos._X * $scope.zoom;
                            $scope.pliney[i][b] = $scope.log[b].LogInfo.Robot[i].Pos._Y * $scope.zoom;
                        }

                    }
                } else {

                    for (i = 0; i < $scope.numRobots; i++) {
                        $scope.plinex[i][$scope.idx] = $scope.log[$scope.idx].LogInfo.Robot[i].Pos._X * $scope.zoom;
                        $scope.pliney[i][$scope.idx] = $scope.log[$scope.idx].LogInfo.Robot[i].Pos._Y * $scope.zoom;
                    }


                }
                $scope.last_idx = $scope.idx;
                $scope.drawLine();
                $scope.drawRobots();


            };

            $scope.refreshSVG = function () {
                $scope.updateValues();
                $timeout($scope.refreshSVG, 1000);

            };

            $scope.play = function () {
                if (!$scope.playvar) {
                    $scope.playvar = 1;
                    refresh($scope.refresh_rate);
                }
            };

            $scope.pause = function () {
                if ($scope.playvar) {
                    $scope.playvar = 0;
                    $timeout($scope.refreshSVG, 1000);
                }
            };

            $scope.stop = function () {
                $scope.idx = 0;
                $scope.playvar = 0;
                refresh(0);
            };

            $scope.$on("$destroy", function(event){
                $scope.idx = 0;
                $scope.playvar = 0;
                refresh(0);
            });

        }
    }
})();
