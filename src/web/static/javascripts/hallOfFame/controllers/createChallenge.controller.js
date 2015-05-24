(function () {
    'use strict';

    angular
        .module('ciberonline.hallOfFame.controllers')
        .controller('CreateChallengeController', CreateChallengeController);

    CreateChallengeController.$inject = ['$scope', 'Round', '$location', 'HallOfFame', 'SoloTrials', 'Competition', 'Notification'];

    function CreateChallengeController($scope, Round, $location, HallOfFame, SoloTrials, Competition, Notification){
        var vm = this;
        vm.getGrid = getGrid;
        vm.getLab = getLab;
        vm.create = create;
        vm.createUpload = createUpload;

        activate();

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

        function getGrid(){
            var grid = document.getElementById("select1").value;
            SoloTrials.getResource(grid).then(getResourceSuccessFn, getResourceErrorFn);
            function getResourceSuccessFn(data){
                vm.grid = data.data;

            }
        }

        function getLab(){
            var lab = document.getElementById("select2").value;
            SoloTrials.getResource(lab).then(getResourceSuccessFn, getResourceErrorFn);
            function getResourceSuccessFn(data){
                vm.lab = data.data;

            }
        }
        function getResourceErrorFn(data){
            console.error(data.data);
        }

        function create(){
            var grid = document.getElementById("select1").value;
            var lab = document.getElementById("select2").value;
            var param = document.getElementById("select3").value;

            console.log(grid);

            Competition.getAllRounds("Hall of fame - Single").then(getHallOfFameSuccessFn, getHallOfFameErrorFn);

            function getHallOfFameSuccessFn(data){
                vm.challenges = data.data;
                console.log(vm.challenges);
                $scope.loader = {
                    loading: true
                };
                Round.createRound(vm.challengeName, "Hall of fame - Single").then(createSuccessFn, createErrorFn);
            }

            function getHallOfFameErrorFn(data){
                console.error(data.data);
            }


            function createSuccessFn(){
                HallOfFame.create("Hall of fame - Single", vm.challengeName, "grid", grid).then(uploadGridSuccessFn, uploadGridErrorFn);

                function uploadGridSuccessFn(){
                    HallOfFame.create("Hall of fame - Single", vm.challengeName, "lab", lab).then(uploadLabSuccessFn, uploadLabErrorFn);

                    function uploadLabSuccessFn(){
                        HallOfFame.create("Hall of fame - Single", vm.challengeName, "param_list", param).then(uploadParamSuccessFn, uploadParamErrorFn);

                        function uploadParamSuccessFn(){
                            $.jGrowl("Challenge successfully created.", {
                                life: 2500,
                                theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                            });
                            $location.url("/admin/challenges");
                        }

                        function uploadParamErrorFn(data){
                            console.error(data.data);
                            $.jGrowl(data.data.message, {
                                life: 5000,
                                theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
                            });
                            Round.destroy(vm.challengeName, "Hall of fame - Single");
                        }

                    }

                    function uploadLabErrorFn(data){
                        console.error(data.data);
                        Round.destroy(vm.challengeName, "Hall of fame - Single");

                    }

                }

                function uploadGridErrorFn(data){
                    console.error(data.data);
                    Round.destroy(vm.challengeName, "Hall of fame - Single");

                }
            }

            function createErrorFn(data){
                console.error(data.data);
                $.jGrowl(data.data.message, {
                    life: 5000,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
                });
            }
        }

        function createUpload(){
            Round.createRound(vm.challengeName, "Hall of fame - Single").then(createSuccessFn, createErrorFn);

            function createSuccessFn(){

                var selectedFile1 = document.getElementById('ParamListUpload').files[0];
                if(selectedFile1 != undefined){
                    uploadParamList();
                }else{
                    $.jGrowl("Param List is Required", {
                        life: 5000,
                        theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
                    });
                    Round.destroy(vm.challengeName, "Hall of fame - Single");
                }
            }

            function createErrorFn(data){
                console.error(data.data);
                $.jGrowl(data.data.message, {
                    life: 5000,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
                });
            }

        }

        function uploadParamList() {
            var selectedFile = document.getElementById('ParamListUpload').files[0];

            Round.uploadParamList(vm.challengeName, selectedFile, "Hall of fame - Single").then(uploadSuccessFn, uploadErrorFn);

            function uploadSuccessFn(){

                var selectedFile2 = document.getElementById('GridUpload').files[0];

                if(selectedFile2 != undefined){
                    uploadGrid();
                }else{
                    $.jGrowl("Grid is Required", {
                        life: 5000,
                        theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
                    });
                    Round.destroy(vm.challengeName, "Hall of fame - Single");
                }
            }

            function uploadErrorFn(data){
                var errors = "";
                if(typeof data.data.detail != "undefined"){
                    errors += data.data.detail;
                }
                else{
                    if (typeof data.data.message == 'object'){
                        for (var value in data.data.message) {
                            errors += "&bull; " + (value.charAt(0).toUpperCase() + value.slice(1)).replace("_", " ") + ":<br/>"
                            for (var error in data.data.message[value]){
                                errors += " &nbsp; "+ data.data.message[value][error] + '<br/>';
                            }
                        }
                    }
                    else{
                        errors+= data.data.message + '<br/>'
                    }
                }
                if(typeof data.data.detail !== 'undefined'){
                    errors += " &nbsp; "+ data.data.detail + '<br/>';
                }
                $.jGrowl(errors, {
                    life: 5000,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
                });
                Round.destroy(vm.challengeName, "Hall of fame - Single");
            }

        }

        function uploadGrid() {
            var selectedFile = document.getElementById('GridUpload').files[0];

            Round.uploadGrid(vm.challengeName, selectedFile, "Hall of fame - Single").then(uploadSuccessFn, uploadErrorFn);

            function uploadSuccessFn(){
                var selectedFile3 = document.getElementById('LabUpload').files[0];
                if(selectedFile3 != undefined){
                    uploadLab();
                }else{
                    $.jGrowl("Lab is Required", {
                        life: 5000,
                        theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
                    });
                    Round.destroy(vm.challengeName, "Hall of fame - Single");
                }


            }

            function uploadErrorFn(data){
                $.jGrowl("File \'" + selectedFile.name + "\' can't be uploaded.", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
                });
                console.error(data.data);
                Round.destroy(vm.challengeName, "Hall of fame - Single");
            }

        }

        function uploadLab() {
            var selectedFile = document.getElementById('LabUpload').files[0];

            Round.uploadLab(vm.challengeName, selectedFile, "Hall of fame - Single").then(uploadSuccessFn, uploadErrorFn);

            function uploadSuccessFn(){
                $location.url("/admin/challenges");


            }

            function uploadErrorFn(data){
                $.jGrowl("File \'" + selectedFile.name + "\' can't be uploaded.", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
                });
                console.error(data.data);
                Round.destroy(vm.challengeName, "Hall of fame - Single");
            }

        }

    }
})();