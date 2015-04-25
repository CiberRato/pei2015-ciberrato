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
        
        var identifier = $routeParams.identifier;

        LogViewer.getLog(identifier).then(getLogSuccess, getLogError);

        function getLogSuccess(log){
            console.log("ACTIVATED");
            console.log("TENHO O FICHEIRO: LOG!");


            $scope.logInfo_obj = log.data.Log;
            $scope.parameters_obj = log.data.Parameters;
            $scope.lab_obj = log.data.Lab;
            $scope.grid_obj = log.data.Grid;
            console.log($scope.logInfo_obj);

            showViewer();
        }
        function getLogError(){
            console.log("ERROR");
        }
        function showViewer(){

            $("#waitawhile").hide("fast");
            $("#row1").show("slow");
            $("#row2").show("slow");
            $("#row3").show("slow");
            $("#row4").show("slow");
            $("#row5").show("slow");

            $scope.zoom = 31.5;

            console.log("OK");
            doIt();
        }

        function isArray(myArray) {
            return myArray.constructor.toString().indexOf("Array") > -1;
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
            if($scope.nBeacon==1){
                ctx1.beginPath();
                ctx1.arc($scope.beacon._X * $scope.zoom, $scope.beacon._Y * $scope.zoom, $scope.zoom + $scope.zoom/15, 0, 2*Math.PI);
                ctx1.fillStyle = $scope.circleBorder;
                ctx1.fill();
                var imageObj = new Image();
                imageObj.onload = function() {
                    ctx1.drawImage(imageObj, $scope.beacon._X * $scope.zoom - $scope.zoom, $scope.beacon._Y * $scope.zoom - $scope.zoom, $scope.zoom*2,$scope.zoom*2 );
                };
                imageObj.src = $scope.cheeseColor;
                ctx1.fill();
                ctx1.stroke();

            }
            else{
                for(i=0;i<$scope.lab_obj.Beacon.length;i++){
                    ctx1.beginPath();
                    ctx1.arc($scope.beacon[i]._X * $scope.zoom, $scope.beacon[i]._Y * $scope.zoom, $scope.zoom + $scope.zoom/15, 0, 2*Math.PI);
                    ctx1.fillStyle = $scope.circleBorder;
                    ctx1.fill();
                    var imageObj = new Image();
                    imageObj.onload = function() {
                        ctx1.drawImage(imageObj, $scope.beacon[i]._X * $scope.zoom - $scope.zoom, $scope.beacon[i]._Y * $scope.zoom - $scope.zoom, $scope.zoom*2,$scope.zoom*2 );
                    };
                    imageObj.src = $scope.cheeseColor;
                    ctx1.fill();
                    ctx1.stroke();
                }
            }
        }

        function drawWalls(){
            var i;
            for (i = 0; i < $scope.lab_obj.Wall.length; i++) {

                if($scope.lab_obj.Wall[i]._Height < $scope.beacon_height){
                    ctx1.fillStyle = $scope.smallWallColor;
                }
                else{
                    ctx1.fillStyle = $scope.greatWallColor;
                }
                ctx1.beginPath();
                var b = 0;
                for(; b < $scope.lab_obj.Wall[i].Corner.length; b++){
                    ctx1.lineTo($scope.lab_obj.Wall[i].Corner[b]._X * $scope.zoom ,$scope.lab_obj.Wall[i].Corner[b]._Y * $scope.zoom);
                }
                ctx1.closePath();
                ctx1.fill();
            }
        }

        $scope.drawRobots=function(){
            ctx2.clearRect(0, 0, c2.width, c2.height);

            var i;
            var x;
            var y;
            var color;
            var dir;
            if($scope.numRobots==1){
                ctx2.beginPath();
                ctx2.arc($scope.robot.Pos._X * $scope.zoom, $scope.robot.Pos._Y * $scope.zoom, $scope.zoom/2, 0, 2 * Math.PI, false);
                ctx2.fillStyle = "rgba(0, 0, 0, 0.0)";
                ctx2.lineWidth = 1;
                ctx2.strokeStyle = $scope.circleBorder;
                ctx2.stroke();
                if($scope.robot.Scores._Collision=='True'){
                    x =  $scope.robot.Pos._X * $scope.zoom - $scope.zoom/2;
                    y =  $scope.robot.Pos._Y * $scope.zoom - $scope.zoom/2;
                    dir = $scope.dir[0];
                    ctx2.save();
                    ctx2.translate(x + $scope.zoom/2,y+ $scope.zoom/2);
                    ctx2.rotate(dir * Math.PI/180);
                    ctx2.drawImage($scope.blackmouse, -$scope.zoom/2, -$scope.zoom/2, $scope.zoom , $scope.zoom );
                    ctx2.fill();
                    ctx2.stroke();
                    ctx2.restore();
                }
                else{
                    x =  $scope.robot.Pos._X * $scope.zoom - $scope.zoom/2;
                    y =  $scope.robot.Pos._Y * $scope.zoom - $scope.zoom/2;
                    color = $scope.mickeyColor[0];
                    dir = $scope.dir[0];
                    ctx2.save();
                    ctx2.translate(x + $scope.zoom/2,y+ $scope.zoom/2);
                    ctx2.rotate(dir * Math.PI/180);
                    ctx2.drawImage(color, -$scope.zoom/2, -$scope.zoom/2, $scope.zoom , $scope.zoom );
                    ctx2.fill();
                    ctx2.stroke();
                    ctx2.restore();
                }

            }
            else {
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
        }

        function doIt() {
            c1.width=$scope.zoom * $scope.lab_obj._Width;
            c1.height=$scope.zoom * $scope.lab_obj._Height;
            c2.width=$scope.zoom * $scope.lab_obj._Width;
            c2.height=$scope.zoom * $scope.lab_obj._Height;
            ctx1.translate(0, $scope.zoom * $scope.lab_obj._Height);
            ctx1.scale(1, -1);
            ctx2.translate(0, $scope.zoom * $scope.lab_obj._Height);
            ctx2.scale(1, -1);

            $scope.velButton = '1x';

            var b = 0;
            var i = 0;

            $scope.slow = 0;
            $scope.playvar = 0;
            /* Parameters Object */
            $scope.param = $scope.parameters_obj;
            /* Map Object */
            $scope.map = $scope.lab_obj;
            /* Grid Object */
            $scope.grid = $scope.grid_obj;
            console.log($scope.grid);
            /* Log Object */
            $scope.log = $scope.logInfo_obj;

            /* Beacons Object */
            $scope.beacon = $scope.lab_obj.Beacon;

            /* Number of Beacons */
            if (isArray($scope.lab_obj.Beacon)) {
                $scope.nBeacon = $scope.lab_obj.Beacon.length;

            }
            else {
                $scope.nBeacon = 1
            }
            /* Find beacon height */
            if ($scope.nBeacon == 1)
                $scope.beacon_height = $scope.lab_obj.Beacon._Height;
            else
                $scope.beacon_height = $scope.lab_obj.Beacon[0]._Height;

            /* Number of Robots */
            //console.log($scope.log);
            if (isArray($scope.log[0].LogInfo.Robot)) {
                $scope.numRobots = $scope.log[0].LogInfo.Robot.length;
            }
            else {
                $scope.numRobots = 1;
            }

            /* Retrieve spawning direction for every robot */
            $scope.dir = [];
            if ($scope.numRobots > 1) {
                for (i = 0; i < $scope.numRobots; i++) {
                    $scope.dir[i] = parseInt($scope.log[0].LogInfo.Robot[i].Pos._Dir) + 90;
                }
            }
            else {
                $scope.dir[0] = parseInt($scope.log[0].LogInfo.Robot.Pos._Dir) + 90;
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

            if ($scope.numRobots==1){
                $scope.pline = "";
                $scope.bclass[0] = 'btn btn-success'
                $scope.toggleText[0] = 'Show';
                $scope.slyne[0] = false;
                $scope.robotColor[0] = $scope.mickeyColor[0];
                $scope.lineColor[0] = $scope.lColor[0];
            }else{
                $scope.pline = [];
                for (i = 0; i < $scope.numRobots; i++) {
                    $scope.pline[i] = "";
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

                    $(".leftGrip").css("left", ($scope.idx * ($scope.map._Width*$scope.zoom)) / $scope.param._SimTime);
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
                $scope.drawRobots();
                $scope.robot = $scope.log[$scope.idx].LogInfo.Robot;
                $scope.time = $scope.log[$scope.idx].LogInfo._Time;

                /* Update directions of every robot */
                if ($scope.numRobots != 1) {
                    for (i = 0; i < $scope.numRobots; i++) {
                        $scope.dir[i] = parseInt($scope.log[$scope.idx].LogInfo.Robot[i].Pos._Dir) + 90;
                    }
                }
                else {
                    $scope.dir[0] = parseInt($scope.log[$scope.idx].LogInfo.Robot.Pos._Dir) + 90;
                }

                /* Calculate visited points line */
                if (($scope.last_idx + 1) != $scope.idx) {
                    if ($scope.numRobots!=1){
                        for (i = 0; i < $scope.numRobots; i++) {
                            $scope.pline[i] = "";
                        }
                    }else{
                        $scope.pline = "";
                    }

                    for (b = 0; b < $scope.idx; b++) {
                        if ($scope.numRobots != 1) {
                            for (i = 0; i < $scope.numRobots; i++) {
                                $scope.pline[i] += $scope.log[b].LogInfo.Robot[i].Pos._X * $scope.zoom + "," + $scope.log[b].LogInfo.Robot[i].Pos._Y * $scope.zoom + " ";
                            }
                        }
                        else {
                            $scope.pline += $scope.log[b].LogInfo.Robot.Pos._X * $scope.zoom + "," + $scope.log[b].LogInfo.Robot.Pos._Y * $scope.zoom + " ";
                        }
                    }
                } else {
                    if ($scope.numRobots != 1) {
                        for (i = 0; i < $scope.numRobots; i++) {
                            $scope.pline[i] += $scope.log[$scope.idx].LogInfo.Robot[i].Pos._X * $scope.zoom + "," + $scope.log[$scope.idx].LogInfo.Robot[i].Pos._Y * $scope.zoom + " ";
                        }
                    }
                    else {
                        $scope.pline += $scope.log[$scope.idx].LogInfo.Robot.Pos._X * $scope.zoom + "," + $scope.log[$scope.idx].LogInfo.Robot.Pos._Y * $scope.zoom + " ";
                    }
                }
                $scope.last_idx = $scope.idx;

            };

            $scope.refreshSVG = function () {
                $scope.updateValues();
                $timeout($scope.refreshSVG, 1000);

            };

            $scope.setMazeColor = function (id) {

                if (id == 1) {
                    $scope.groundColor = 'black';
                    $scope.cheeseColor = 'static/img/svg/cheese.svg';
                    $scope.circleBorder = '#00ffff';
                    $scope.greatWallColor = '#008000';
                    $scope.smallWallColor = '#0000ff';
                    $scope.gridColor = '#cfd4db';

                }
                if (id == 2) {
                    $scope.groundColor = 'darkgrey';
                    $scope.cheeseColor = 'static/img/svg/blackCheese.svg';
                    $scope.circleBorder = '#cfd4db';
                    $scope.greatWallColor = '#353535';
                    $scope.smallWallColor = '#727272';
                    $scope.gridColor = '#cfd4db';

                }

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
        }
    }
})();
