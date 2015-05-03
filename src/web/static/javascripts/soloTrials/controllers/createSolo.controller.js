(function(){

    'use strict';

    angular
        .module('ciberonline.soloTrials.controllers')
        .controller('CreateSoloController', CreateSoloController);

    CreateSoloController.$inject = ['SoloTrials', '$routeParams', 'Round'];

    function CreateSoloController(SoloTrials, $routeParams, Round){
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
            }

            function createErrorFn(data){
                console.error(data.data);
                var errors = "";
                for (var value in data.data.message) {
                    errors += "&bull; " + (value.charAt(0).toUpperCase() + value.slice(1)).replace("_", " ") + ":<br/>"
                    for (var error in data.data.message[value]){
                        errors += " &nbsp; "+ data.data.message[value][error] + '<br/>';
                    }
                }
                $.jGrowl(errors, {
                    life: 5000,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
                });
            }
        }

    }

})();