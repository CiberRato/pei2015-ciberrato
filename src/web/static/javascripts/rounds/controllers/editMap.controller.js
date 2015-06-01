(function () {
    'use strict';

    angular
        .module('ciberonline.rounds.controllers')
        .controller('EditMapController', EditMapController);

    EditMapController.$inject = ['$scope', '$routeParams', 'Round'];

    function EditMapController($scope, $routeParams, Round){
        var x2js = new X2JS();

        function labConvertXml2JSon() {
            hasMap = true;

            return JSON.stringify(x2js.xml_str2json($scope.codeLab));
        }

        function gridConvertXml2JSon() {
            hasGrid = true;

            return JSON.stringify(x2js.xml_str2json($scope.codeGrid));
        }

        var vm = this;
        var hasGrid = false;
        var hasMap = false;
        vm.getCodeGrid = getCodeGrid;
        vm.getCodeLab = getCodeLab;
        vm.getCodeParam = getCodeParam;
        var c3 = document.getElementById("layer3");
        var ctx = c3.getContext("2d");
        $scope.zoom = 50;

        activate();


        function activate(){
            $scope.loader = {
                loading: false
            };

            vm.competitionName = $routeParams.competitionName;
            vm.roundName = $routeParams.roundName;
            Round.getFiles(vm.roundName, vm.competitionName).then(getFilesSuccessFn, getFilesErrorFn);

            function getFilesSuccessFn(data){
                vm.files = data.data;

                console.log(vm.files);
                if(vm.files.grid.file == ''){
                    $scope.codeGrid = '';

                    var file = new Blob([$scope.codeGrid], {type: 'text/plain'});
                    console.log(file);

                    Round.uploadGrid(vm.roundName, file, vm.competitionName, 'grid.xml').then(successUploadGrid, errorUploadGrid);

                }else{
                    Round.getFile(vm.roundName, vm.competitionName, "grid").then(getGridSuccessFn, getGridErrorFn);

                }

                function successUploadGrid(){
                    Round.getFile(vm.roundName, vm.competitionName, "grid").then(getGridSuccessFn, getGridErrorFn);

                }
                function errorUploadGrid(data){
                    console.error(data.data);
                }

                function getGridSuccessFn(data) {
                    $scope.codeGrid = data.data;
                    console.log('ola');
                    if(vm.files.lab.file == ''){
                        $scope.codeLab = '';

                        var file = new Blob([$scope.codeLab], {type: 'text/plain'});
                        console.log(file);
                        Round.uploadLab(vm.roundName, file, vm.competitionName, 'lab.xml').then(successUploadLab, errorUploadLab);

                    }else{
                        Round.getFile(vm.roundName, vm.competitionName, "lab").then(getLabSuccessFn, getLabErrorFn);

                    }
                }
                function successUploadLab(){
                    Round.getFile(vm.roundName, vm.competitionName, "lab").then(getLabSuccessFn, getLabErrorFn);

                }
                function errorUploadLab(data){
                    console.error(data.data);
                }

                function getLabSuccessFn(data) {
                    $scope.codeLab = data.data;
                    console.log('ola');

                    if(vm.files.param_list.file == ''){
                        $scope.codeParam = '';

                        var file = new Blob([$scope.codeParam], {type: 'text/plain'});
                        console.log(file);

                        Round.uploadParamList(vm.roundName, file, vm.competitionName, 'param_list.xml').then(successUploadParam, errorUploadParam);

                    }else{
                        Round.getFile(vm.roundName, vm.competitionName, "param_list").then(getParamSuccessFn, getParamErrorFn);

                    }
                }
                function successUploadParam(){
                    Round.getFile(vm.roundName, vm.competitionName, "param_list").then(getParamSuccessFn, getParamErrorFn);

                }
                function errorUploadParam(data){
                    console.error(data.data);
                }

                function getParamSuccessFn(data){
                    $scope.codeParam = data.data;
                    $scope.gridLoaded();
                    $scope.labLoaded();

                    $scope.loader.loading=true;

                }

                function getParamErrorFn(){

                }

                function getLabErrorFn(){

                }



                function getGridErrorFn(){

                }


            }

            function getFilesErrorFn(data) {
                console.error(data.data);
            }

        }

        function prepareParamters(){
            if($scope.map !== null){
                c3.width=$scope.zoom * $scope.map.Lab._Width;
                c3.height=$scope.zoom * $scope.map.Lab._Height;

                ctx.translate(0, $scope.zoom * $scope.map.Lab._Height);
                ctx.scale(1, -1);

                /* Beacons Object */
                $scope.beacon = $scope.map.Lab.Beacon;

                /* Number of Beacons */
                try{
                    $scope.nBeacon = $scope.map.Lab.Beacon.length;
                    $scope.beacon_height =  $scope.map.Lab.Beacon[0]._Height;
                }
                catch(e){
                    $scope.nBeacon = 1;
                    $scope.beacon_height =  $scope.map.Lab.Beacon._Height;
                }


                /* Set Maze Colors */
                $scope.groundColor = 'black';
                $scope.cheeseColor = 'static/img/svg/cheese.png';
                $scope.circleBorder = '#00ffff';
                $scope.greatWallColor = '#008000';
                $scope.smallWallColor = '#0000ff';
                $scope.gridColor = '#cfd4db';
            }

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
            if($scope.grid !== null){
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

        }
        function drawBeacon(){
            if($scope.map !== null){
                var i;
                var dx = [];
                var dy =[];
                var dWidth = [];
                var dHeight = [];
                if($scope.nBeacon == 1){
                    ctx.beginPath();
                    ctx.arc($scope.map.Lab.Beacon._X * $scope.zoom, $scope.map.Lab.Beacon._Y * $scope.zoom, $scope.zoom * $scope.map.Lab.Target._Radius + $scope.zoom/15, 0, 2*Math.PI);
                    ctx.fillStyle = $scope.circleBorder;
                    ctx.fill();

                    dx[0] = ($scope.map.Lab.Beacon._X * $scope.zoom) - ($scope.zoom*$scope.map.Lab.Target._Radius);
                    dy[0] = ($scope.map.Lab.Beacon._Y * $scope.zoom) - ($scope.zoom*$scope.map.Lab.Target._Radius);
                    dWidth[0] = $scope.zoom*$scope.map.Lab.Target._Radius*2;
                    dHeight[0] = $scope.zoom*$scope.map.Lab.Target._Radius*2;

                    ctx.fill();
                    ctx.stroke();
                }
                else{
                    for(i=0;i<$scope.map.Lab.Beacon.length;i++){
                        ctx.beginPath();
                        ctx.arc($scope.map.Lab.Beacon[i]._X * $scope.zoom, $scope.map.Lab.Beacon[i]._Y * $scope.zoom, $scope.zoom * $scope.map.Lab.Target[i]._Radius + $scope.zoom/15, 0, 2*Math.PI);
                        ctx.fillStyle = $scope.circleBorder;
                        ctx.fill();

                        dx[0] = ($scope.map.Lab.Beacon[i]._X * $scope.zoom) - ($scope.zoom*$scope.map.Lab.Target[i]._Radius);
                        dy[0] = ($scope.map.Lab.Beacon[i]._Y * $scope.zoom) - ($scope.zoom*$scope.map.Lab.Target[i]._Radius);
                        dWidth[0] = $scope.zoom*$scope.map.Lab.Target[i]._Radius*2;
                        dHeight[0] = $scope.zoom*$scope.map.Lab.Target[i]._Radius*2;

                        var imageObj = new Image();
                        imageObj.onload = function() {
                            ctx.drawImage(imageObj, dx, dy, dWidth, dHeight);
                        };
                        imageObj.src = $scope.cheeseColor;
                        ctx.fill();
                        ctx.stroke();
                    }
                }
                var imageObj = new Image();
                imageObj.onload = function() {
                    for(i=0;i<$scope.nBeacon;i++){
                        ctx.drawImage(imageObj, dx[i], dy[i], dWidth[i], dHeight[i]);
                    }
                };
                imageObj.src = $scope.cheeseColor;
                ctx.fill();
                ctx.stroke();

            }


        }

        function drawWalls(){
            if($scope.map !== null){
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

        }



        function getCodeGrid(){
            hasGrid = true;
            var a = $scope.codeGrid;
            console.log($scope.codeGrid);
            $scope.grid = angular.fromJson(gridConvertXml2JSon());
            console.log($scope.grid);

            var file = new Blob([a], {type: 'text/plain'});

            Round.uploadGrid(vm.roundName, file, vm.competitionName, vm.files.grid.file).then(success, error);

            function success(){
                if (hasMap){
                    prepareParamters();
                    drawMap();
                    drawGrid();
                }
                $.jGrowl("File \'" + vm.files.grid.file + "\' has been updated.", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                });
            }
            function error(data){
                console.error(data.data);
            }
        }
        function getCodeLab(){
            hasMap = true;
            var a = $scope.codeLab;
            $scope.map = angular.fromJson(labConvertXml2JSon());
            console.log($scope.map);

            var file = new Blob([a], {type: 'text/plain'});
            console.log(file);

            Round.uploadLab(vm.roundName, file, vm.competitionName, vm.files.lab.file).then(success, error);

            function success(){
                if (hasGrid){
                    prepareParamters();
                    drawMap();
                    drawGrid();
                }
                $.jGrowl("File \'" + vm.files.lab.file + "\' has been updated.", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                });            }
            function error(data){
                console.error(data.data);
            }
        }
        function getCodeParam(){
            var a = $scope.codeParam;
            console.log(a);

            var file = new Blob([a], {type: 'text/plain'});

            Round.uploadParamList(vm.roundName, file, vm.competitionName, vm.files.param_list.file).then(success, error);

            function success(){
                $.jGrowl("File \'" + vm.files.param_list.file + "\' has been updated.", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                });            }
            function error(data){
                console.error(data.data);
            }
        }
        $scope.gridChanged = function(){
            if(hasMap && hasGrid){
                console.log('Grid changed');
                $scope.grid = angular.fromJson(gridConvertXml2JSon());
                console.log($scope.grid);
                prepareParamters();
                drawMap();
                drawGrid();
            }

        };

        $scope.gridLoaded = function(){
            $scope.grid = angular.fromJson(gridConvertXml2JSon());
            if (hasMap){
                prepareParamters();
                drawMap();
                drawGrid();
            }
        };

        $scope.labChanged = function(){
            if(hasMap && hasGrid) {
                console.log('lab changed');
                $scope.map = angular.fromJson(labConvertXml2JSon());
                console.log($scope.map);
                prepareParamters();
                drawMap();
                drawGrid();
            }

        };

        $scope.labLoaded = function(){
            $scope.map = angular.fromJson(labConvertXml2JSon());
            if (hasGrid){
                prepareParamters();
                drawMap();
                drawGrid();
            }
        };
        /*$scope.codeGrid.getSession().on('change', function () {
            console.log($scope.codeGrid.getSession().getValue());
            prepareParamters();
             drawMap();
             drawGrid();
        });*/

    }
})();


