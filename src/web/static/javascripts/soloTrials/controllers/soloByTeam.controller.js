(function(){

    'use strict';

    angular
        .module('ciberonline.soloTrials.controllers')
        .controller('SoloByTeamController', SoloByTeamController);

    SoloByTeamController.$inject = ['SoloTrials', '$routeParams', '$timeout', '$scope', 'Notification'];

    function SoloByTeamController(SoloTrials, $routeParams, $timeout, $scope, Notification){
        var vm = this;
        var hasGrid = false;
        var hasMap = false;
        $scope.zoom = 50;
        vm.competitionName = $routeParams.identifier;
        vm.teamName = $routeParams.teamName;
        vm.deleteSoloTrial = deleteSoloTrial;
        vm.getGrid = getGrid;
        vm.getLab = getLab;
        activate();

        function activate(){
            $scope.loader = {
                loading: false
            };
            Notification.activateNotifications();

            SoloTrials.getByTeam(vm.competitionName).then(getByTeamSuccessFn, getByTeamErrorFn);

            function getByTeamSuccessFn(data){
                vm.solos = data.data;
                console.log(vm.solos);
                $scope.loader = {
                    loading: true
                };
            }


            function getByTeamErrorFn(data){
                console.error(data.data);
            }


        }

        function prepareParameters(){
            console.log(vm.id);
            $scope.c3 = document.getElementById("layer3");
            console.log($scope.c3.id);
            $scope.ctx = $scope.c3.getContext("2d");

            doIt();

        }

        function drawMap(){
            console.log("drawMAp");
            $scope.ctx.clearRect(0, 0, $scope.c3.width, $scope.c3.height);
            $scope.ctx.rect(0,0, $scope.c3.width, $scope.c3.height);
            $scope.ctx.fillStyle=$scope.groundColor;
            $scope.ctx.fill();
            drawWalls();
        }

        function drawGrid(){
            var i;
            console.log("drawGrid");

            for(i=0;i<$scope.grid.Grid.Position.length;i++) {
                $scope.ctx.beginPath();
                $scope.ctx.arc($scope.grid.Grid.Position[i]._X*$scope.zoom, $scope.grid.Grid.Position[i]._Y*$scope.zoom, $scope.zoom/2, 0, 2 * Math.PI, false);
                $scope.ctx.fillStyle = $scope.gridColor;
                $scope.ctx.fill();
                $scope.ctx.lineWidth = 2;
                $scope.ctx.strokeStyle = $scope.circleBorder;
                $scope.ctx.stroke();
            }

        }

        function drawBeacon(){
            var i;
            console.log("drawBeacon");

            for(i=0;i<$scope.map.Lab.Beacon.length;i++){
                console.log($scope.map.Lab.Beacon[i]);
                $scope.ctx.beginPath();
                $scope.ctx.arc($scope.map.Lab.Beacon[i]._X * $scope.zoom, $scope.map.Lab.Beacon[i]._Y * $scope.zoom, $scope.zoom * $scope.map.Lab.Target[i]._Radius + $scope.zoom/15, 0, 2*Math.PI);
                $scope.ctx.fillStyle = $scope.circleBorder;
                $scope.ctx.fill();

                var dx = ($scope.map.Lab.Beacon[i]._X * $scope.zoom) - ($scope.zoom*$scope.map.Lab.Target[i]._Radius);
                var dy = ($scope.map.Lab.Beacon[i]._Y * $scope.zoom) - ($scope.zoom*$scope.map.Lab.Target[i]._Radius);
                var dWidth = $scope.zoom*$scope.map.Lab.Target[i]._Radius*2;
                var dHeight = $scope.zoom*$scope.map.Lab.Target[i]._Radius*2;

                var imageObj = new Image();
                imageObj.onload = function() {
                    $scope.ctx.drawImage(imageObj, dx, dy, dWidth, dHeight);
                };
                imageObj.src = $scope.cheeseColor;
                $scope.ctx.fill();
                $scope.ctx.stroke();
            }
            drawGrid();


        }

        function drawWalls(){
            var i;
            console.log("drawWalls");

            for (i = 0; i < $scope.map.Lab.Wall.length; i++) {

                if($scope.map.Lab.Wall[i]._Height < $scope.beacon_height){
                    $scope.ctx.fillStyle = $scope.smallWallColor;
                }
                else{
                    $scope.ctx.fillStyle = $scope.greatWallColor;
                }
                $scope.ctx.beginPath();
                var b = 0;
                for(; b < $scope.map.Lab.Wall[i].Corner.length; b++){
                    $scope.ctx.lineTo($scope.map.Lab.Wall[i].Corner[b]._X * $scope.zoom ,$scope.map.Lab.Wall[i].Corner[b]._Y * $scope.zoom);
                }
                $scope.ctx.closePath();
                $scope.ctx.fill();
            }
            drawBeacon();

        }


        function doIt(){
            console.log("doIT");

            $scope.c3.width=$scope.zoom * $scope.map.Lab._Width;
            $scope.c3.height=$scope.zoom * $scope.map.Lab._Height;

            $scope.ctx.translate(0, $scope.zoom * $scope.map.Lab._Height);
            $scope.ctx.scale(1, -1);

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
            drawMap();
        }

        function deleteSoloTrial(name){
            SoloTrials.removeSoloTrial(name).then(removeSoloTrialSuccessFn, removeSoloTrialErrorFn);

            function removeSoloTrialSuccessFn(){
                $.jGrowl("Solo Trial has been removed successfully.", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                });
                $timeout(function(){
                    SoloTrials.getByTeam(vm.competitionName).then(getByTeamSuccessFn, getByTeamErrorFn);

                    function getByTeamSuccessFn(data){
                        vm.solos = data.data;
                        console.log(vm.solos);
                    }


                    function getByTeamErrorFn(data){
                        console.error(data.data);
                    }                });
            }

            function removeSoloTrialErrorFn(data){
                console.error(data.data);
                $.jGrowl("Solo Trial could not be removed.", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
                });
            }
        }

        function getGrid(grid){

            SoloTrials.getResource(grid).then(getResourceSuccessFn, getResourceErrorFn);

            function getResourceSuccessFn(data){
                hasGrid = true;

                vm.grid = data.data;
                $scope.grid=data.data;
                if(hasMap && hasGrid){
                    hasGrid = false;
                    hasMap = false;
                    prepareParameters();

                }
            }
        }

        function getLab(lab){

            SoloTrials.getResource(lab).then(getResourceSuccessFn, getResourceErrorFn);

            function getResourceSuccessFn(data){
                hasMap = true;

                vm.lab = data.data;
                $scope.map=data.data;
                if(hasMap && hasGrid){
                    hasGrid = false;
                    hasMap = false;
                    prepareParameters();

                }
            }

        }

        function getResourceErrorFn(data){
            console.error(data.data);
        }

    }

})();