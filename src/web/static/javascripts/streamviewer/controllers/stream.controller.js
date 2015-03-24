(function(){
    'use strict';

    angular
        .module('ciberonline.streamviewer.controllers')
        .controller('StreamViewer', StreamViewer);

    StreamViewer.$inject = ['$location', '$scope', '$routeParams','Round', 'Authentication', 'Profile', 'LogViewer', '$timeout'];

    function StreamViewer($location, $scope, $routeParams, Round, Authentication, Profile, StreamViewer, $timeout){
        var username;

        var parameters;
        var logInfo;
        var grid;
        var lab;
        var logBuff_obj = [];

        getLabJson();

        function getLabJson(){
            // caso precise de autenticação
            var authenticatedAccount = Authentication.getAuthenticatedAccount();
            username = authenticatedAccount.username;

            console.log("ACTIVATED");

            StreamViewer.getLabViewer().then(getLabSuccessFn, getErrorFn);
        }
        function getLabSuccessFn(data){
            console.log("TENHO O FICHEIRO: lab!");
            lab = data.data;
            StreamViewer.getParametersViewer().then(getParametersSuccessFn, getErrorFn);
        }
        function getParametersSuccessFn(data){
            console.log("TENHO O FICHEIRO: parameters!");
            parameters = data.data;
            StreamViewer.getGridViewer().then(getGridSuccessFn, getErrorFn);
        }
        function getGridSuccessFn(data){
            console.log("TENHO O FICHEIRO: grid!");
            grid = data.data;
            CiberWebSocket();
        }
        function getErrorFn(data){
            console.log("FODEU tudo!");
        }

        function CiberWebSocket(){
            if ("WebSocket" in window) {
                // alert("WebSocket is supported by your Browser!");
                // Let us open a web socket
                var opened = false;

                var ws = new WebSocket("ws://127.0.0.1:7777/ws");
                var div = document.getElementById('show');

                ws.onopen = function () {
                    ws.send("OK");
                    opened = true;
                };
                ws.onmessage = function (evt) {
                    var received_msg = evt.data;
                    //div.innerHTML = div.innerHTML + received_msg;
                    //console.log(received_msg);
                    logBuff_obj.push(JSON.parse(received_msg));
                    console.log(logBuff_obj.length);

                    if(logBuff_obj.length==10){
                        $("#waitawhile").hide("fast");
                        $("#row1").show("slow");
                        $("#row2").show("slow");
                        $("#row3").show("slow");
                        $("#row4").show("slow");
                        $("#row5").show("slow");
                        doIt();
                    }
                };
                ws.onclose = function () {
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

        function convertToStringPoints(cornerList, zoom){
            var out = "";
            var b = 0;
            for(; b<cornerList.Corner.length; b++){
                out+= cornerList.Corner[b]._X*zoom + "," + cornerList.Corner[b]._Y*zoom + " ";
            }
            return out;
        }

        function isArray(myArray) {
            return myArray.constructor.toString().indexOf("Array") > -1;
        }

        function doIt() {
            if(isArray(logBuff_obj[0].LogInfo.Robot)){
                $scope.numRobots = logBuff_obj[0].LogInfo.Robot.length;
            }
            else{
                $scope.numRobots = 1;
            }

            /* Zoom variable (30->Standard) */
            $scope.zoom = 30;

            /* JSON to Object */
            var lab_obj = angular.fromJson(lab);
            var grid_obj = angular.fromJson(grid);
            var parameters_obj = angular.fromJson(parameters);

            var b = 0;
            var i = 0;
            
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

            /* Beacons Object */
            $scope.beacon = lab_obj.Lab.Beacon;

            /* Number of Beacons */
            if(isArray($scope.map.Beacon)){
                $scope.nBeacon = $scope.map.Beacon.length;
            }
            else{
                $scope.nBeacon = 1
            }

            /* Find beacon height */
            if($scope.nBeacon == 1)
                $scope.beacon_height = lab_obj.Lab.Beacon._Height;
            else
                $scope.beacon_height = lab_obj.Lab.Beacon[0]._Height;


            /* Retrieve spawning direction for every robot */
            $scope.dir = [];
            if($scope.numRobots>1){
                for(i=0; i<$scope.numRobots; i++){
                    $scope.dir[i] = parseInt(logBuff_obj[0].LogInfo.Robot[i].Pos._Dir) + 90;
                }
            }
            else{
                $scope.dir[0] = parseInt(logBuff_obj[0].LogInfo.Robot.Pos._Dir) + 90;
            }


            /* Robots Object */
            $scope.robot = logBuff_obj[0].LogInfo.Robot;

            /* Time Value */
            $scope.time = logBuff_obj[0].LogInfo._Time;

            /* Refresh rate value for each iteration */
            $scope.refresh_rate = $scope.param._CycleTime;

            $scope.idx = 1;

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
                try{
                    $scope.updateValues();

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
                $scope.robot = logBuff_obj[$scope.idx].LogInfo.Robot;
                $scope.time = logBuff_obj[$scope.idx].LogInfo._Time;

                /* Update directions of every robot */
                if($scope.numRobots != 1){
                    for(i=0; i<$scope.numRobots; i++){
                        $scope.dir[i] = parseInt(logBuff_obj[$scope.idx].LogInfo.Robot[i].Pos._Dir) + 90;
                    }
                }
                else {
                    $scope.dir[0] = parseInt(logBuff_obj[$scope.idx].LogInfo.Robot.Pos._Dir) + 90;
                }
            };

            $scope.refreshSVG = function(){
                $scope.updateValues();
                $timeout($scope.refreshSVG, 1000);

            };

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
            $scope.play();

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
        }
    }
})();
