(function () {
    'use strict';

    angular
        .module('ciberonline.rounds.controllers')
        .controller('EditMapController', EditMapController);

    EditMapController.$inject = ['$scope', '$routeParams', 'Round'];

    function EditMapController($scope, $routeParams, Round){
        var vm = this;
        vm.getCodeGrid = getCodeGrid;
        vm.getCodeLab = getCodeLab;
        vm.getCodeParam = getCodeParam;
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
                $scope.aceOptions = {mode: 'xml', theme: 'monokai'};
                Round.getFile(vm.roundName, vm.competitionName, "grid").then(getGridSuccessFn, getGridErrorFn);

                function getGridSuccessFn(data){
                    $scope.codeGrid = data.data;
                    Round.getFile(vm.roundName, vm.competitionName, "lab").then(getLabSuccessFn, getLabErrorFn);

                    function getLabSuccessFn(data){
                        $scope.codeLab = data.data;
                        Round.getFile(vm.roundName, vm.competitionName, "param_list").then(getParamSuccessFn, getParamErrorFn);

                        function getParamSuccessFn(data){
                            $scope.codeParam = data.data;
                            $scope.loader.loading=true;

                        }

                        function getParamErrorFn(data){
                            console.error(data.data);
                        }

                    }

                    function getLabErrorFn(data){
                        console.error(data.data);
                    }

                }

                function getGridErrorFn(data){
                    console.error(data.data);
                }


            }

            function getFilesErrorFn(data) {
                console.error(data.data);
            }

        }

        function getCodeGrid(){
            var a = $scope.codeGrid;
            console.log(a);

            var file = new Blob([a], {type: 'text/plain'});

            Round.uploadGrid(vm.roundName, file, vm.competitionName, vm.files.grid.file).then(success, error);

            function success(){
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
            var a = $scope.codeLab;
            console.log(a);

            var file = new Blob([a], {type: 'text/plain'});

            Round.uploadLab(vm.roundName, file, vm.competitionName, vm.files.lab.file).then(success, error);

            function success(){
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



    }
})();


