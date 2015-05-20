(function(){

    'use strict';

    angular
        .module('ciberonline.soloTrials.controllers')
        .controller('SoloByTeamController', SoloByTeamController);

    SoloByTeamController.$inject = ['SoloTrials', '$routeParams', '$timeout', '$scope'];

    function SoloByTeamController(SoloTrials, $routeParams, $timeout, $scope){
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

        function prepareParameters(){
            console.log('5');
            var c3 = document.getElementById("layer3");
            var ctx = c3.getContext("2d");

            doIt(c3,ctx);

        }

        function drawMap(c3,ctx){

            ctx.clearRect(0, 0, c3.width, c3.height);
            ctx.rect(0,0, c3.width, c3.height);
            ctx.fillStyle=$scope.groundColor;
            ctx.fill();
            drawWalls(c3,ctx);
            drawBeacon(c3,ctx);
        }

        function drawGrid(c3,ctx){
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

        function drawBeacon(c3,ctx){
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

        function drawWalls(c3,ctx){
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

        function activate(){
            $scope.loader = {
                loading: false
            };
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
        function doIt(c3,ctx){
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
            drawMap(c3,ctx);
            drawGrid(c3,ctx);
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
                console.log(data.data);
                if(hasMap == true && hasGrid == true){
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
                console.log(data.data);
                if(hasMap == true && hasGrid == true){
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