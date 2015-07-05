(function () {
    'use strict';

    angular
        .module('ciberonline.hallOfFame.controllers')
        .controller('AllChallengesController', AllChallengesController);

    AllChallengesController.$inject = ['$scope', 'Competition', '$timeout', 'Round', 'Authentication', 'Agent', 'HallOfFame'];

    function AllChallengesController($scope, Competition, $timeout, Round, Authentication, Agent, HallOfFame){
        var x2js = new X2JS();
        var c3;
        var ctx;
        var vm = this;
        vm.deleteChallenge = deleteChallenge;
        var authenticatedAccount = Authentication.getAuthenticatedAccount();
        vm.username = authenticatedAccount.username;
        vm.launchTrial = launchTrial;
        vm.getFiles = getFiles;
        vm.show = [];
        var hasGrid = false;
        var hasMap = false;

        $scope.zoom = 50;
        activate();
        function labConvertXml2JSon(lab) {
            hasMap = true;

            return JSON.stringify(x2js.xml_str2json(lab));
        }

        function gridConvertXml2JSon(grid) {
            hasGrid = true;

            return JSON.stringify(x2js.xml_str2json(grid));
        }

        function prepareParamters(){


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

        function drawWalls(){
            var i;
            if($scope.map.Lab.hasOwnProperty('Wall')){
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


        function activate(){
            $scope.loader = {
                loading: false
            };

            Competition.getAllRounds("Hall of fame - Single").then(getHallOfFameSuccessFn, getHallOfFameErrorFn);

            function getHallOfFameSuccessFn(data){
                vm.challenges = data.data;
                console.log(vm.challenges);

                Agent.getByUser(vm.username).then(getAgentsSuccessFn, getAgentsErrorFn);
                function getAgentsSuccessFn(data){
                    vm.agents = data.data;
                    for(var i=0; i<vm.agents.length; i++){
                        if(vm.agents[i].agent_name != "Remote"){
                            vm.show.push(vm.agents[i]);

                        }
                    }
                    console.log(vm.show);
                    $scope.loader = {
                        loading: true
                    };
                }

                function getAgentsErrorFn(data){
                    console.error(data.data);
                }

            }

            function getHallOfFameErrorFn(data){
                console.error(data.data);
            }



        }

        function getFiles(name){
            console.log('aaqui');
            c3 = document.getElementById("layer3");
            ctx = c3.getContext("2d");
            Round.getFile(name, "Hall of fame - Single", 'grid').then(getGridSuccessFn, getGridErrorFn);

            function getGridSuccessFn(data){
                vm.grid = data.data;
                $scope.grid = angular.fromJson(gridConvertXml2JSon(data.data));
                console.log($scope.grid);
                Round.getFile(name, "Hall of fame - Single", 'lab').then(getLabSuccessFn, getLabErrorFn);

                function getLabSuccessFn(data){
                    vm.lab = data.data;
                    $scope.map = angular.fromJson(labConvertXml2JSon(data.data));
                    console.log($scope.map);
                    prepareParamters();
                    drawMap();
                    drawGrid();


                }

                function getLabErrorFn(data){
                    console.error(data.data);
                }

            }


            function getGridErrorFn(data){
                console.error(data.data);
            }
        }


        function deleteChallenge(name){
            Round.destroy(name, "Hall of fame - Single").then(deleteChallengeSuccessFn, deleteChallengeErrorFn);

            function deleteChallengeSuccessFn(){
                $.jGrowl("Challenge has been removed successfully.", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                });
                $timeout(function() {
                    Competition.getAllRounds("Hall of fame - Single").then(getHallOfFameSuccessFn, getHallOfFameErrorFn);

                    function getHallOfFameSuccessFn(data) {
                        vm.challenges = data.data;
                        console.log(vm.challenges);
                        $scope.loader = {
                            loading: true
                        };
                    }

                    function getHallOfFameErrorFn(data) {
                        console.error(data.data);
                    }
                });
            }

            function deleteChallengeErrorFn(data){
                console.error(data.data);
                $.jGrowl("Challenge could not be removed.", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
                });
            }
        }

        function launchTrial(roundName){
            var tmp = document.getElementById('select'+roundName);
            tmp = tmp.options[tmp.selectedIndex].value;
            console.log(tmp);
            var agent = tmp.substr(0,tmp.indexOf(','));
            var team = tmp.substr(tmp.indexOf(',') + 1);

            HallOfFame.launchTrial(roundName, agent, team).then(launchTrialSuccessFn, launchTrialErrorFn);

            function launchTrialSuccessFn(data){
                $.jGrowl("Trial has been created successfully", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                });
                console.log(data.data);
                $timeout(function(){
                    Round.getTrials(roundName, "Hall of fame - Single").then(getTrialsSuccessFn, getTrialsErrorFn);

                    function getTrialsSuccessFn(data){
                        vm.trials = data.data;
                        console.log(vm.trials);

                        Agent.getByUser(vm.username).then(getAgentsSuccessFn, getAgentsErrorFn);

                        function getAgentsSuccessFn(data){
                            vm.agents = data.data;
                            $scope.loader = {
                                loading: true
                            };
                        }

                        function getAgentsErrorFn(data){
                            console.error(data.data);
                        }


                    }

                    function getTrialsErrorFn(data) {
                        console.error(data.data);
                    }
                });
            }

            function launchTrialErrorFn(data){
                console.error(data.data);
                $.jGrowl(data.data.message, {
                    life: 5000,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
                });
            }
        }



    }
})();
