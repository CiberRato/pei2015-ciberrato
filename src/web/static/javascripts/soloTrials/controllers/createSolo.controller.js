(function(){

    'use strict';

    angular
        .module('ciberonline.soloTrials.controllers')
        .controller('CreateSoloController', CreateSoloController);

    CreateSoloController.$inject = ['SoloTrials', '$routeParams', 'Round', '$location'];

    function CreateSoloController(SoloTrials, $routeParams, Round, $location){
        var vm = this;
        vm.competitionName = $routeParams.identifier;
        vm.teamName = $routeParams.teamName;
        vm.create = create;
        activate();

        function activate(){
            Round.getResources().then(getResourcesSuccessFn, getResourcesErrorFn);

            function getResourcesSuccessFn(data){
                vm.resources = data.data;
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

    }

})();