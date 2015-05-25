(function(){
    'use strict';

    angular
        .module('ciberonline.streamviewer.controllers')
        .controller('StreamViewer', StreamViewer);

    StreamViewer.$inject = ['$location', '$scope', '$routeParams','Round', 'Competition', 'Profile', 'StreamViewer', '$timeout', '$dragon', 'Authentication'];

    function StreamViewer($location, $scope, $routeParams, Round, Competition, Profile, StreamViewer, $timeout, $dragon, Authentication){

        var parameters;
        $scope.simulation;
        var grid;
        var lab;
        var identifier = $routeParams.identifier;
        $scope.logBuff_obj = [];

        var c1 = document.getElementById("layer1");
        var c2 = document.getElementById("layer2");
        var c3 = document.getElementById("layer3");
        var ctx = c3.getContext("2d");
        var ctx2 = c2.getContext("2d");
        /* Zoom variable (50->Standard) */
        $scope.zoom = 50;
        activate();
        function activate(){
            Round.getTrial(identifier).then(getSimulationSuccessFn, getSimulationErrorFn);
        }
        function getSimulationSuccessFn(data){
            $scope.simulation = data.data;
            console.log("ACTIVATED");
            Competition.getCompetition($scope.simulation.competition_name).then(getCompetitionSucess, getCompetitionError);
        }

        function getCompetitionSucess(data){
            $scope.competition = data.data;
            StreamViewer.getLabViewer($scope.simulation.round_name, $scope.simulation.competition_name).then(getLabSuccessFn, getErrorFn);

        }

        function getCompetitionError(data){
            console.error(data.data);
            $location.path('/panel/');
        }

        function getSimulationErrorFn(data){
            console.error(data.data);
            $location.path('/panel/');
        }

        function getLabSuccessFn(data){
            console.log("TENHO O FICHEIRO: lab!");
            console.log(data.data);
            $scope.map = data.data;
            StreamViewer.getParametersViewer($scope.simulation.round_name, $scope.simulation.competition_name).then(getParametersSuccessFn, getErrorFn);

        }
        function getParametersSuccessFn(data){
            console.log("TENHO O FICHEIRO: parameters!");
            console.log(data.data);
            $scope.param = data.data;
            StreamViewer.getGridViewer($scope.simulation.round_name, $scope.simulation.competition_name).then(getGridSuccessFn, getErrorFn);

        }
        function getGridSuccessFn(data){
            console.log("TENHO O FICHEIRO: grid!");
            console.log(data.data);
            $scope.grid = data.data;
            PrepareParameters();
            $scope.drawMap();
            ctx = c1.getContext("2d");
            CiberWebSocket();
        }
        function getErrorFn(data){
            console.log("ERRO!");
        }

        function PrepareParameters(){
            
            c3.width=$scope.zoom * $scope.map.Lab._Width;
            c3.height=$scope.zoom * $scope.map.Lab._Height;

            ctx.translate(0, $scope.zoom * $scope.map.Lab._Height);
            ctx.scale(1, -1);

            /* Beacons Object */
            $scope.beacon = $scope.map.Lab.Beacon;

            /* Number of Beacons */
          	$scope.nBeacon = $scope.map.Lab.Beacon.length;
           

            /* Find beacon height */
            $scope.beacon_height = $scope.map.Lab.Beacon[0]._Height;

            /* Set Maze Colors */
            $scope.groundColor = 'black';
            $scope.cheeseColor = 'static/img/svg/cheese.png';
            $scope.circleBorder = '#00ffff';
            $scope.greatWallColor = '#008000';
            $scope.smallWallColor = '#0000ff';
            $scope.gridColor = '#cfd4db';


        }

        function CiberWebSocket(){
            $dragon.onReady(function() {
                var user = Authentication.getAuthenticatedAccount();
                var simulation_id = $scope.simulation.identifier;

                $dragon.subscribe('stream_trial', 'notifications', {
                    'user': user,
                    'identifier': simulation_id
                }, function (context, data) {
                    // any thing that happens after successfully subscribing
                    console.log("// any thing that happens after successfully subscribing");
                }, function (context, data) {
                    // any thing that happens if subscribing failed
                    console.log("// any thing that happens if subscribing failed");
                });
                /*
                $dragon.onChannelMessage(function(channels, data) {
                    console.log("STREAM");

                    try{
                        $scope.logBuff_obj.push(JSON.parse(data.data.message));
                    }catch(e){
                        console.log(data);
                    }

                    if($scope.logBuff_obj.length==20){
                        $("#waitawhile").hide("fast");
                        $("#row1").show("slow");
                        $("#row2").show("slow");
                        $("#row5").show("slow");

                        doIt();

                        $scope.play();
                        console.log('play');
                    }
                });
               */
            });
        }

        $scope.drawMap=function(){

            ctx.clearRect(0, 0, c1.width, c1.height);
            ctx.rect(0,0, c1.width, c1.height);
            ctx.fillStyle=$scope.groundColor;
            ctx.fill();
            drawWalls();
            drawBeacon();
            drawGrid();
        }

        function drawGrid(){
            var i;
            for(i=0;i<$scope.grid.Grid.Position.length;i++) {
                ctx.beginPath();
                ctx.arc($scope.grid.Grid.Position[i]._X*$scope.zoom, $scope.grid.Grid.Position[i]._Y*$scope.zoom, $scope.zoom/2, 0, 2 * Math.PI, false);
                ctx.fillStyle = $scope.gridColor;
                ctx.fill();
                ctx.lineWidth = 2;
                ctx.strokeStyle = $scope.circleBorder;
                ctx.stroke();
            }
        }

        function drawBeacon(){
            var i;
            
            for(i=0;i<$scope.map.Lab.Beacon.length;i++){
                console.log($scope.map.Lab.Beacon[i]);
                ctx.beginPath();
                ctx.arc($scope.map.Lab.Beacon[i]._X * $scope.zoom, $scope.map.Lab.Beacon[i]._Y * $scope.zoom, $scope.zoom * $scope.map.Lab.Target[i]._Radius + $scope.zoom/15, 0, 2*Math.PI);
                ctx.fillStyle = $scope.circleBorder;
                ctx.fill();

                var dx = ($scope.map.Lab.Beacon[i]._X * $scope.zoom) - ($scope.zoom*$scope.map.Lab.Target[i]._Radius);
                var dy = ($scope.map.Lab.Beacon[i]._Y * $scope.zoom) - ($scope.zoom*$scope.map.Lab.Target[i]._Radius);
                var dWidth = $scope.zoom*$scope.map.Lab.Target[i]._Radius*2;
                var dHeight = $scope.zoom*$scope.map.Lab.Target[i]._Radius*2;

                var imageObj = new Image();
                imageObj.onload = function() {
                    ctx.drawImage(imageObj, dx, dy, dWidth, dHeight);
                };
                imageObj.src = $scope.cheeseColor;
                ctx.fill();
                ctx.stroke();
            }
            
        }

        function drawWalls(){
            var i;
            for (i = 0; i < $scope.map.Lab.Wall.length; i++) {

                if($scope.map.Lab.Wall[i]._Height < $scope.beacon_height){
                    ctx.fillStyle = $scope.smallWallColor;
                }
                else{
                    ctx.fillStyle = $scope.greatWallColor;
                }
                ctx.beginPath();
                var b = 0;
                for(; b < $scope.map.Lab.Wall[i].Corner.length; b++){
                    ctx.lineTo($scope.map.Lab.Wall[i].Corner[b]._X * $scope.zoom ,$scope.map.Lab.Wall[i].Corner[b]._Y * $scope.zoom);
                }
                ctx.closePath();
                ctx.fill();
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
            c1.width=$scope.zoom * $scope.map.Lab._Width;
            c1.height=$scope.zoom * $scope.map.Lab._Height;
            c2.width=$scope.zoom * $scope.map.Lab._Width;
            c2.height=$scope.zoom * $scope.map.Lab._Height;
            ctx.translate(0, $scope.zoom * $scope.map.Lab._Height);
            ctx.scale(1, -1);
            ctx2.translate(0, $scope.zoom * $scope.map.Lab._Height);
            ctx2.scale(1, -1);

            
            $scope.numRobots = $scope.logBuff_obj[0].LogInfo.Robot.length;
            

            $scope.finalResults = [];

            var b = 0;
            var i = 0;

            $scope.slow = 0;
            $scope.playvar = 0;


            /* Retrieve spawning direction for every robot */
            $scope.dir = [];
            for(i=0; i<$scope.numRobots; i++){
                $scope.dir[i] = parseInt($scope.logBuff_obj[0].LogInfo.Robot[i].Pos._Dir) + 90;
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
            $scope.mickeysFINAL =['static/img/svg/mickey_red_smile.png','static/img/svg/mickey_green_smile.png','static/img/svg/mickey_blue_smile.png','static/img/svg/mickey_yellow_smile.png','static/img/svg/mickey_orange_smile.png'];

            /* Set Line Colors */
            $scope.lColor = ['#E04F5F', '#5FBF60', '#29BAF7', '#eaea3d', '#f28d14'];

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
                try {

                    if ($scope.param.Parameters._SimTime == $scope.logBuff_obj[$scope.idx].LogInfo._Time) {
                        $scope.playvar = -1;
                        console.log('parou tudo');
                        
                        $scope.finalResults = $scope.logBuff_obj[$scope.idx].LogInfo.Robot
                        var swapped;
                        do {
                            swapped = false;
                            for (var i = 0; i < $scope.finalResults.length - 1; i++) {
                                if ($scope.finalResults[i].Scores._Score > $scope.finalResults[i + 1].Scores._Score) {
                                    var temp = $scope.finalResults[i];
                                    var temp2 = $scope.mickeysFINAL[i];

                                    $scope.finalResults[i] = $scope.finalResults[i + 1];
                                    $scope.mickeysFINAL[i] = $scope.mickeysFINAL[i + 1];

                                    $scope.finalResults[i + 1] = temp;
                                    $scope.mickeysFINAL[i + 1] = temp2;
                                    swapped = true;
                                }
                            }
                        } while (swapped);
                        
                        

                    }
                }catch(TypeError){

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
                }catch(TypeError){

                }

                if($scope.playvar){
                    refresh($scope.refresh_rate);
                }

                if($scope.playvar == -1){

                    //$("#row1").hide("slow");
                    $("#row2").hide("slow");
                    $("#finalResults").show("slow");

                }
            };

            /* Update Viewer Values */
            $scope.updateValues = function(){
                $scope.robot = $scope.logBuff_obj[$scope.idx].LogInfo.Robot;
                $scope.time = $scope.logBuff_obj[$scope.idx].LogInfo._Time;

                /* Update directions of every robot */
                
                for(i=0; i<$scope.numRobots; i++){
                    $scope.dir[i] = parseInt($scope.logBuff_obj[$scope.idx].LogInfo.Robot[i].Pos._Dir) + 90;
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
