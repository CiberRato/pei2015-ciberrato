(function(){
    'use strict';

    angular
        .module('ciberonline.streamviewer.controllers')
        .controller('StreamViewer', StreamViewer);

    StreamViewer.$inject = ['$location', '$scope', '$routeParams','Round', 'Authentication', 'Profile', 'StreamViewer', '$timeout'];

    function StreamViewer($location, $scope, $routeParams, Round, Authentication, Profile, StreamViewer, $timeout){
        var username;
        var x2js = new X2JS();
        var parameters;
        var simulation;
        var grid;
        var lab;
        var identifier = $routeParams.identifier;
        $scope.logBuff_obj = [];

        var c1 = document.getElementById("layer1");
        var ctx1 = c1.getContext("2d");
        var c2 = document.getElementById("layer2");
        var ctx2 = c2.getContext("2d");

        Round.getTrial(identifier).then(getSimulationSuccessFn, getSimulationErrorFn);
        function getSimulationSuccessFn(data){
            simulation = data.data;
            //console.log("simulation" + simulation);
            console.log("ACTIVATED");

            StreamViewer.getLabViewer(simulation.round_name).then(getLabSuccessFn, getErrorFn);
        }

        function getSimulationErrorFn(data){
            console.error(data.data);
            $location.path('/panel/');
        }

        function getLabSuccessFn(data){
            console.log("TENHO O FICHEIRO: lab!");
            lab = x2js.xml_str2json(data.data);

            $scope.lab_obj = angular.fromJson(lab);
            StreamViewer.getParametersViewer(simulation.round_name).then(getParametersSuccessFn, getErrorFn);
        }
        function getParametersSuccessFn(data){
            console.log("TENHO O FICHEIRO: parameters!");
            parameters = x2js.xml_str2json(data.data);

            $scope.parameters_obj = angular.fromJson(parameters);
            StreamViewer.getGridViewer(simulation.round_name).then(getGridSuccessFn, getErrorFn);
        }
        function getGridSuccessFn(data){
            console.log("TENHO O FICHEIRO: grid!");
            grid = x2js.xml_str2json(data.data);

            $scope.grid_obj = angular.fromJson(grid);
            CiberWebSocket();
        }
        function getErrorFn(data){
            console.error
            console.log("ERRO!");
        }

        function CiberWebSocket(){
            if ("WebSocket" in window) {
                console.log('entrei na funçao');

                var opened = false;

                var ws = new WebSocket("ws://127.0.0.1:7777/ws");

                ws.onopen = function () {

                    ws.send("OK");
                    opened = true;
                };
                ws.onmessage = function (evt) {

                    var received_msg = evt.data;

                    $scope.logBuff_obj.push(JSON.parse(received_msg));

                    if($scope.logBuff_obj.length>20){
                        $("#waitawhile").hide("fast");
                        $("#row1").show("slow");
                        $("#row2").show("slow");
                        $("#row5").show("slow");

                        /* Zoom variable (50->Standard) */
                        $scope.zoom = 50;
                        doIt();

                        $scope.play();
                        console.log('play');
                    }
                };
                ws.onclose = function () {
                    console.log('on close');
                    if(!opened){
                        CiberWebSocket();
                    }
                };
            }
            else {
                // The browser doesn't support WebSocket
                alert("WebSocket NOT supported by your Browser!");
            }
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
                for(i=0;i<$scope.lab_obj.Lab.Beacon.length;i++){
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
            for (i = 0; i < $scope.lab_obj.Lab.Wall.length; i++) {

                if($scope.lab_obj.Lab.Wall[i]._Height < $scope.beacon_height){
                    ctx1.fillStyle = $scope.smallWallColor;
                }
                else{
                    ctx1.fillStyle = $scope.greatWallColor;
                }
                ctx1.beginPath();
                var b = 0;
                for(; b < $scope.lab_obj.Lab.Wall[i].Corner.length; b++){
                    ctx1.lineTo($scope.lab_obj.Lab.Wall[i].Corner[b]._X * $scope.zoom ,$scope.lab_obj.Lab.Wall[i].Corner[b]._Y * $scope.zoom);
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
            c1.width=$scope.zoom * $scope.lab_obj.Lab._Width;
            c1.height=$scope.zoom * $scope.lab_obj.Lab._Height;
            c2.width=$scope.zoom * $scope.lab_obj.Lab._Width;
            c2.height=$scope.zoom * $scope.lab_obj.Lab._Height;
            ctx1.translate(0, $scope.zoom * $scope.lab_obj.Lab._Height);
            ctx1.scale(1, -1);
            ctx2.translate(0, $scope.zoom * $scope.lab_obj.Lab._Height);
            ctx2.scale(1, -1);

            if(isArray($scope.logBuff_obj[0].LogInfo.Robot)){
                $scope.numRobots = $scope.logBuff_obj[0].LogInfo.Robot.length;
            }
            else{
                $scope.numRobots = 1;
            }

            $scope.finalResults = [];

            var b = 0;
            var i = 0;

            $scope.slow = 0;
            $scope.playvar = 0;

            /* Parameters Object */
            $scope.param=$scope.parameters_obj.Parameters;

            /* Map Object */
            $scope.map = $scope.lab_obj.Lab;

            /* Grid Object */
            $scope.grid = $scope.grid_obj.Grid;

            /* Beacons Object */
            $scope.beacon = $scope.lab_obj.Lab.Beacon;

            /* Number of Beacons */
            if(isArray($scope.map.Beacon)){
                $scope.nBeacon = $scope.map.Beacon.length;
            }
            else{
                $scope.nBeacon = 1
            }

            /* Find beacon height */
            if($scope.nBeacon == 1)
                $scope.beacon_height = $scope.lab_obj.Lab.Beacon._Height;
            else
                $scope.beacon_height = $scope.lab_obj.Lab.Beacon[0]._Height;


            /* Retrieve spawning direction for every robot */
            $scope.dir = [];
            if($scope.numRobots>1){
                for(i=0; i<$scope.numRobots; i++){
                    $scope.dir[i] = parseInt($scope.logBuff_obj[0].LogInfo.Robot[i].Pos._Dir) + 90;
                }
            }
            else{
                $scope.dir[0] = parseInt($scope.logBuff_obj[0].LogInfo.Robot.Pos._Dir) + 90;
            }


            /* Robots Object */
            $scope.robot = $scope.logBuff_obj[0].LogInfo.Robot;

            /* Time Value */
            $scope.time = $scope.logBuff_obj[0].LogInfo._Time;

            /* Refresh rate value for each iteration */
            $scope.refresh_rate = $scope.param._CycleTime;

            $scope.idx = 1;

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

            $scope.drawMap();
            $scope.drawRobots();

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
            };

            /* Update timeline */
            var tick = function() {

                if($scope.logBuff_obj[$scope.logBuff_obj.length-1].LogInfo._Time == $scope.logBuff_obj[$scope.idx].LogInfo._Time){
                    $scope.playvar=-1;
                    console.log('parou tudo');
                    if($scope.numRobots != 1) {
                        $scope.finalResults = $scope.logBuff_obj[$scope.idx].LogInfo.Robot
                        var swapped;
                        do {
                            swapped = false;
                            for (var i = 0; i < $scope.finalResults.length - 1; i++) {
                                if ($scope.finalResults[i].Scores._Score > $scope.finalResults[i + 1].Scores._Score) {
                                    var temp = $scope.finalResults[i];
                                    var temp2 = $scope.mickeyColor[i];

                                    $scope.finalResults[i] = $scope.finalResults[i + 1];
                                    $scope.mickeyColor[i] = $scope.mickeyColor[i + 1];

                                    $scope.finalResults[i + 1] = temp;
                                    $scope.mickeyColor[i + 1] = temp2;
                                    swapped = true;
                                }
                            }
                        } while (swapped);
                        ;
                    }

                }
                try{
                    $scope.updateValues();

                    if($scope.playvar){
                        if ($scope.logBuff_obj.length - 1 > $scope.idx + 50){
                            $scope.idx = $scope.logBuff_obj.length - 20;
                        }
                        else{
                            $scope.idx++;
                        }
                    }
                    //console.log("IDX"+$scope.idx);
                }catch(TypeError){

                }

                if($scope.playvar){
                    refresh($scope.refresh_rate);
                }

                if($scope.playvar == -1){

                    $("#row1").hide("slow");
                    $("#row2").hide("slow");
                    $("#finalResults").show("slow");

                }
            };

            /* Update Viewer Values */
            $scope.updateValues = function(){
                $scope.robot = $scope.logBuff_obj[$scope.idx].LogInfo.Robot;
                $scope.time = $scope.logBuff_obj[$scope.idx].LogInfo._Time;

                /* Update directions of every robot */
                if($scope.numRobots != 1){
                    for(i=0; i<$scope.numRobots; i++){
                        $scope.dir[i] = parseInt($scope.logBuff_obj[$scope.idx].LogInfo.Robot[i].Pos._Dir) + 90;
                    }
                }
                else {
                    $scope.dir[0] = parseInt($scope.logBuff_obj[$scope.idx].LogInfo.Robot.Pos._Dir) + 90;
                }
                $scope.drawRobots();

            };

            $scope.refreshSVG = function(){
                $scope.updateValues();
                $timeout($scope.refreshSVG, 1000);

            };

            $scope.setMazeColor = function(id){

                if(id == 1){
                    $scope.groundColor = 'black';
                    $scope.cheeseColor = 'static/img/svg/cheese.svg';
                    $scope.circleBorder = '#00ffff';
                    $scope.greatWallColor = '#008000';
                    $scope.smallWallColor = '#0000ff';
                    $scope.gridColor = '#cfd4db';

                }
                if(id == 2){
                    $scope.groundColor = 'darkgrey';
                    $scope.cheeseColor = 'static/img/svg/blackCheese.svg';
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

        }
    }
})();
