(function(){
    'use strict';

    angular
        .module('ciberonline.logviewer.controllers')
        .controller('LogViewer', LogViewer);

    LogViewer.$inject = ['$location', '$routeParams','Round', 'Authentication', 'Profile', 'LogViewer', '$timeout'];

    function LogViewer($location, $routeParams, Round, Authentication, Profile, LogViewer, $timeout){
        var vm = this;
        var username;

        var logInfo;
        var lab;
        var parameters;
        var grid;

        getLabJson();

        function getLabJson(){
            // caso precise de autenticação
            var authenticatedAccount = Authentication.getAuthenticatedAccount();
            username = authenticatedAccount.username;

            console.log("ACTIVATED");

            LogViewer.getLabViewer().then(getLabSuccessFn, getErrorFn);
        }
        function getLabSuccessFn(data){
            console.log("TENHO O FICHEIRO: lab!");
            lab = data.data;
            LogViewer.getParametersViewer().then(getParametersSuccessFn, getErrorFn);
        }
        function getParametersSuccessFn(data){
            console.log("TENHO O FICHEIRO: parameters!");
            parameters = data.data;
            LogViewer.getGridViewer().then(getGridSuccessFn, getErrorFn);
        }
        function getGridSuccessFn(data){
            console.log("TENHO O FICHEIRO: grid!");
            grid = data.data;
            LogViewer.getLogViewer().then(getLogSuccessFn, getErrorFn);
        }
        function getLogSuccessFn(data){
            logInfo = data.data;
            console.log("TENHO TUDO CARALHO!");
            showViewer();
        }
        function getErrorFn(data){
            console.log("FODEU tudo!");
        }
        function showViewer(){
            $("#waitawhile").hide("fast");
            $("#row1").show("slow");
            $("#row2").show("slow");
            $("#row3").show("slow");
            $("#row4").show("slow");
            $("#row5").show("slow");

            // Call methods and such...
            var highlightMin = Math.random() * 20,
                highlightMax = highlightMin + Math.random() * 80;
            $('.nstSlider').nstSlider({
                "left_grip_selector": ".leftGrip",
                "value_changed_callback": function(cause, leftValue, rightValue) {
                    try{
                        var scope = angular.element('[ng-controller=ctrl]').scope();
                        scope.idx = leftValue;

                    }catch(TypeError){}
                }
            }, 'highlight_range', highlightMin, highlightMax);
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
        function doIt(){
            /* Zoom variable (30->Standard) */
            vm.zoom = 30;
            vm.increments = 1;
            vm.velButton = '1x';

            var i;

            /* JSON to Object */
            var lab_obj = angular.fromJson(lab);
            var grid_obj = angular.fromJson(grid);
            var parameters_obj = angular.fromJson(parameters);
            var logInfo_obj = angular.fromJson(logInfo);

            var b = 0;

            vm.slow = 0;
            vm.playvar = 0;

            /* Convert wall points to be integrated in SVG */
            for(i=0; i<lab_obj.Lab.Wall.length; i++){
                lab_obj.Lab.Wall[i].str = convertToStringPoints(lab_obj.Lab.Wall[i], vm.zoom);
            }

            /* Parameters Object */
            vm.param=parameters_obj.Parameters;

            /* Map Object */
            console.log(lab_obj.Lab);
            vm.map = lab_obj.Lab;
            console.log(vm.map);

            /* Grid Object */
            vm.grid = grid_obj.Grid;

            /* Log Object */
            vm.log = logInfo_obj.Log.LogInfo;

            /* Beacons Object */
            vm.beacon = lab_obj.Lab.Beacon;

            /* Number of Beacons */
            if(isArray(vm.map.Beacon)){
                vm.nBeacon = vm.map.Beacon.length;
            }
            else{
                vm.nBeacon = 1
            }

            /* Find beacon height */
            if(vm.nBeacon == 1)
                vm.beacon_height = lab_obj.Lab.Beacon._Height;
            else
                vm.beacon_height = lab_obj.Lab.Beacon[0]._Height;

            /* Number of Robots */
            if(isArray(vm.log[0].Robot)){
                vm.numRobots = vm.log[0].Robot.length;
            }
            else{
                vm.numRobots = 1;
            }

            /* Retrieve spawning direction for every robot */
            vm.dir = [];
            if(vm.numRobots>1){
                for(i=0; i<vm.numRobots; i++){
                    vm.dir[i] = parseInt(vm.log[0].Robot[i].Pos._Dir) + 90;
                }
            }
            else{
                vm.dir[0] = parseInt(vm.log[0].Robot.Pos._Dir) + 90;
            }


            /* Robots Object */
            vm.robot = vm.log[0].Robot;

            /* Time Value */
            vm.time = vm.log[0]._Time;

            /* Refresh rate value for each iteration */
            vm.refresh_rate = vm.param._CycleTime;

            vm.idx = 1;
            vm.last_idx = 0;

            /* Set Robots Colors */
            vm.mickeyColor = ['static/img/svg/mickey_red_smile.svg','static/img/svg/mickey_green_smile.svg','static/img/svg/mickey_blue_smile.svg','static/img/svg/mickey_yellow_smile.svg','static/img/svg/mickey_orange_smile.svg'];

            /* Set Line Colors */
            vm.lColor = ['#E04F5F','#5FBF60','#29BAF7','#eaea3d','#f28d14'];

            /* Set Maze Colors */
            vm.groundColor = 'black';
            vm.cheeseColor = 'static/img/svg/cheese.svg';
            vm.circleBorder = '#00ffff';
            vm.greatWallColor = '#008000';
            vm.smallWallColor = '#0000ff';
            vm.gridColor = '#cfd4db';

            /* Line points */
            vm.pline = [];

            /* Line Toggled */
            vm.slyne = [];

            /* Line Button Text */
            vm.toggleText = [];

            /* Line Button Class */
            vm.bclass = [];

            /* Robot Color */
            vm.robotColor = [];

            /* Line Color */
            vm.lineColor = [];

            for(i=0; i<vm.numRobots; i++){
                vm.pline[i] = "";
                vm.bclass[i] = 'btn btn-success'
                vm.toggleText[i] = 'Show';
                vm.slyne[i] = false;
                if (i>4){
                    vm.robotColor[i] = vm.mickeyColor[0];
                    vm.lineColor[i] = vm.lColor[0];
                }
                else{
                    vm.robotColor[i] = vm.mickeyColor[i];
                    vm.lineColor[i] = vm.lColor[i];
                }
            }

            vm.activeV = function(str) {
                if (str=='1x'){
                    vm.velButton = '1x';
                    vm.refresh_rate=50;
                    vm.slow=0;
                }else if (str=='2x'){
                    vm.velButton = '2x';
                    vm.refresh_rate=25;
                    vm.slow=0;
                }else if (str=='4x'){
                    vm.velButton = '4x';
                    vm.refresh_rate=12.5;
                    vm.slow=0;
                }else if (str=='18x'){
                    vm.velButton = '18x';
                    vm.refresh_rate=400;
                    vm.slow=1;
                }else if (str=='14x'){
                    vm.velButton = '14x';
                    vm.refresh_rate=100;
                    vm.slow=0;
                }
            };

            vm.toggle = function(index) {
                vm.toggleText[index] = vm.slyne[index] ? 'Show' : 'Hide';
                if (vm.bclass[index] === 'btn btn-success')
                    vm.bclass[index] = 'btn btn-danger';
                else
                    vm.bclass[index] = 'btn btn-success';
                vm.slyne[index] = !vm.slyne[index];
            };


            var refresh = function(refresh_rate){
                $timeout(tick, refresh_rate);
            };

            /* Update timeline */
            var tick = function() {
                try{
                    vm.updateValues();

                    $(".leftGrip").css("left", (vm.idx*820)/vm.param._SimTime);
                    if(vm.play){
                        vm.idx++;
                    }
                }catch(TypeError){
                    vm.pause();
                }
                if(vm.playvar){
                    refresh(vm.refresh_rate);
                }
            };

            /* Update Viewer Values */
            vm.updateValues = function(){
                vm.robot = vm.log[vm.idx].Robot;
                vm.time = vm.log[vm.idx]._Time;

                /* Update directions of every robot */
                if(vm.numRobots != 1) {
                    for (i = 0; i < vm.numRobots; i++) {
                        vm.dir[i] = parseInt(vm.log[vm.idx].Robot[i].Pos._Dir) + 90;
                    }
                }
                else{
                    vm.dir[0] = parseInt(vm.log[vm.idx].Robot.Pos._Dir) + 90;
                }

                /* Calculate visited points line */
                if((vm.last_idx+1)!=vm.idx){

                    for(i=0; i<vm.numRobots; i++){
                        vm.pline[i] = "";
                    }
                    for(b=0;b<vm.idx;b++){
                        if(vm.numRobots != 1){
                            for(i=0; i<vm.numRobots; i++){
                                vm.pline[i] += vm.log[b].Robot[i].Pos._X*vm.zoom + "," + vm.log[b].Robot[i].Pos._Y*vm.zoom + " ";
                            }
                        }
                        else{
                            vm.pline[0] += vm.log[b].Robot.Pos._X*vm.zoom + "," + vm.log[b].Robot.Pos._Y*vm.zoom + " ";
                        }
                    }
                }else {
                    if(vm.numRobots != 1) {
                        for (i = 0; i < vm.numRobots; i++) {
                            vm.pline[i] += vm.log[vm.idx].Robot[i].Pos._X * vm.zoom + "," + vm.log[vm.idx].Robot[i].Pos._Y * vm.zoom + " ";
                        }
                    }
                    else{
                        vm.pline[0] += vm.log[vm.idx].Robot.Pos._X * vm.zoom + "," + vm.log[vm.idx].Robot.Pos._Y * vm.zoom + " ";
                    }
                }
                vm.last_idx = vm.idx;

            };

            vm.refreshSVG = function(){
                vm.updateValues();
                $timeout(vm.refreshSVG, 1000);

            };

            vm.setMazeColor = function(id){

                if(id == 1){
                    vm.groundColor = 'black';
                    vm.cheeseColor = 'img/svg/cheese.svg';
                    vm.circleBorder = '#00ffff';
                    vm.greatWallColor = '#008000';
                    vm.smallWallColor = '#0000ff';
                    vm.gridColor = '#cfd4db';

                }
                if(id == 2){
                    vm.groundColor = 'darkgrey';
                    vm.cheeseColor = 'img/svg/blackCheese.svg';
                    vm.circleBorder = '#cfd4db';
                    vm.greatWallColor = '#353535';
                    vm.smallWallColor = '#727272';
                    vm.gridColor = '#cfd4db';

                }

            };
            vm.setIncrements = function(id){

                if(id == 1){
                    vm.increments = 1;
                }
                if(id == 2){
                    vm.increments = 10;
                }
                if(id == 3){
                    vm.increments = 100;
                }

            };

            vm.play = function() {
                if(!vm.playvar){
                    vm.playvar = 1;
                    refresh(vm.refresh_rate);
                }
            };

            vm.pause = function(){
                if(vm.playvar){
                    vm.playvar = 0;
                    $timeout(vm.refreshSVG, 1000);
                }
            };

            vm.stop = function(){
                vm.idx = 0;
                vm.playvar = 0;
                refresh(0);
            };
            vm.teste = "TEST";
        }
    }
})();
