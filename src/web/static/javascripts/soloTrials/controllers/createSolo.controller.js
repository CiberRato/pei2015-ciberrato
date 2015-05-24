(function(){

    'use strict';

    angular
        .module('ciberonline.soloTrials.controllers')
        .controller('CreateSoloController', CreateSoloController);

    CreateSoloController.$inject = ['SoloTrials', '$routeParams', 'Round', '$location', '$scope', 'Notification'];

    function CreateSoloController(SoloTrials, $routeParams, Round, $location, $scope, Notification){
        var vm = this;
        var hasGrid = false;
        var hasMap = false;
        var c3 = document.getElementById("layer5");
        var ctx = c3.getContext("2d");
        $scope.zoom = 50;
        vm.competitionName = $routeParams.identifier;
        vm.teamName = $routeParams.teamName;
        vm.create = create;
        vm.getGrid = getGrid;
        vm.getLab = getLab;
        activate();

        function prepareParamters(){

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

        function drawMap(){

            ctx.clearRect(0, 0, c3.width, c3.height);
            ctx.rect(0,0, c3.width, c3.height);
            ctx.fillStyle=$scope.groundColor;
            ctx.fill();
            drawWalls();
            drawBeacon();
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

        function activate(){
            $scope.loader = {
                loading: false
            };

            Notification.activateNotifications();

            Round.getResources().then(getResourcesSuccessFn, getResourcesErrorFn);

            function getResourcesSuccessFn(data){
                vm.resources = data.data;
                console.log(vm.resources);
                $scope.loader = {
                    loading: true
                };
            }

            function getResourcesErrorFn(data){
                console.error(data.data);
            }

        }

        function create(){
            var grid = document.getElementById("select1").value;
            var lab = document.getElementById("select2").value;
            var param = document.getElementById("select3").value;

            SoloTrials.create(vm.competitionName, grid, lab, param).then(createSuccessFn, createErrorFn);

            function createSuccessFn(){
                $.jGrowl("Solo Trial successfully created.", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                });
                $location.url("/panel/" + vm.teamName + "/" + vm.competitionName + "/soloTrials");
            }

            function createErrorFn(data){
                console.error(data.data);
                $.jGrowl(data.data.message, {
                    life: 5000,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
                });
            }
        }

        function getGrid(){
            hasGrid = true;
            var grid = document.getElementById("select1").value;
            SoloTrials.getResource(grid).then(getResourceSuccessFn, getResourceErrorFn);
            function getResourceSuccessFn(data){
                vm.grid = data.data;
                $scope.grid=data.data;

                if (hasMap){
                    prepareParamters();
                    drawMap();
                    drawGrid();
                }



            }
        }

        function getLab(){
            hasMap = true;
            var lab = document.getElementById("select2").value;
            SoloTrials.getResource(lab).then(getResourceSuccessFn, getResourceErrorFn);
            function getResourceSuccessFn(data){
                vm.lab = data.data;
                $scope.map=data.data;

                if (hasGrid){
                    prepareParamters();
                    drawMap();
                    drawGrid();
                }
            }
        }
        function getResourceErrorFn(data){
            console.error(data.data);
        }

    }

})();