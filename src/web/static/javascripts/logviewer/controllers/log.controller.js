(function(){
    'use strict';

    angular
        .module('ciberonline.logviewer.controllers')
        .controller('LogViewer', LogViewer);

    LogViewer.$inject = ['$location', '$scope', '$routeParams','Round', 'Authentication', 'Profile', 'LogViewer', '$timeout'];

    function LogViewer($location, $scope, $routeParams, Round, Authentication, Profile, LogViewer, $timeout){
        var logInfo_obj;
        var lab_obj;
        var parameters_obj;
        var grid_obj;

        var identifier = $routeParams.identifier;

        LogViewer.getLog(identifier).then(getLogSuccess, getLogError);

        function getLogSuccess(log){
            console.log("ACTIVATED");
            console.log("TENHO O FICHEIRO: LOG!");

            //console.log(log);
            logInfo_obj = log.data.Log;
            parameters_obj = log.data.Parameters;
            lab_obj = log.data.Lab;
            grid_obj = log.data.Grid;

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

            console.log("OK");
            doIt();
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
            /* Zoom variable (30->Standard) */
            $scope.zoom = 30;
            $scope.velButton = '1x';

            var b = 0;
            var i = 0;

            $scope.slow = 0;
            $scope.playvar = 0;

            //console.log(lab_obj);
            /* Convert wall points to be integrated in SVG */
            for (i = 0; i < lab_obj.Wall.length; i++) {
                //console.log(lab_obj);
                lab_obj.Wall[i].str = convertToStringPoints(lab_obj.Wall[i], $scope.zoom);
            }

            /* Parameters Object */
            $scope.param = parameters_obj;

            /* Map Object */
            $scope.map = lab_obj;
            /* --- slider --- */



            /* Grid Object */
            $scope.grid = grid_obj;

            /* Log Object */
            $scope.log = logInfo_obj;

            /* Beacons Object */
            $scope.beacon = lab_obj.Beacon;

            /* Number of Beacons */
            if (isArray($scope.map.Beacon)) {
                $scope.nBeacon = $scope.map.Beacon.length;
            }
            else {
                $scope.nBeacon = 1
            }

            /* Find beacon height */
            if ($scope.nBeacon == 1)
                $scope.beacon_height = lab_obj.Beacon._Height;
            else
                $scope.beacon_height = lab_obj.Beacon[0]._Height;

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

            /* Set Robots Colors */
            $scope.mickeyColor = ['static/img/svg/mickey_red_smile.svg', 'static/img/svg/mickey_green_smile.svg', 'static/img/svg/mickey_blue_smile.svg', 'static/img/svg/mickey_yellow_smile.svg', 'static/img/svg/mickey_orange_smile.svg'];

            /* Set Line Colors */
            $scope.lColor = ['#E04F5F', '#5FBF60', '#29BAF7', '#eaea3d', '#f28d14'];

            /* Set Maze Colors */
            $scope.groundColor = 'black';
            $scope.cheeseColor = 'static/img/svg/cheese.svg';
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

                    $(".leftGrip").css("left", ($scope.idx * 820) / $scope.param._SimTime);
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
                //console.log($scope.robot); O QUE É ISTO?
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
