(function(){

    'use strict';

    angular
        .module('ciberonline.rounds.controllers')
        .controller('DetailRoundController', DetailRoundController);

    DetailRoundController.$inject = ['$location', '$route', '$routeParams', 'Competition', 'Round', 'Authentication'];

    function DetailRoundController($location, $route, $routeParams, Competition, Round, Authentication){
        var vm = this;

        vm.models = {
            selected: null,
            lists: {"Available": [], "Simulation": []}
        };

        // Generate initial model
        for (var i = 1; i <= 3; ++i) {
            vm.models.lists.Available.push({label: "Item A" + i});
            vm.models.lists.Simulation.push({label: "Item B" + i});
        }
        console.log(vm.models);

        vm.createSimulation = createSimulation;
        vm.associateAgent = associateAgent;
        vm.identifier;
        vm.roundName = $routeParams.name;
        vm.uploadParamList = uploadParamList;
        vm.uploadGrid = uploadGrid;
        vm.uploadLab = uploadLab;
        activate();

        function activate() {
            Round.getSimulations(vm.roundName).then(getSimulationsSuccessFn, getSimulationsErrorFn);
            Round.getAgents(vm.roundName).then(getAgentsSuccessFn, getAgentsErrorFn);
            Round.getRound(vm.roundName).then(getRoundSuccessFn, getRoundErrorFn);

            function getSimulationsSuccessFn(data){
                vm.simulations = data.data;
            }

            function getSimulationsErrorFn(data){
                console.error(data.data);
                $location.path('/panel/');
            }

            function getAgentsSuccessFn(data){
                vm.agents = data.data;
                console.log(vm.agents);
            }

            function getAgentsErrorFn(data){
                console.error(data.data);
                $location.path('/panel/');
            }

            function getRoundSuccessFn(data){
                vm.round = data.data;
            }

            function getRoundErrorFn(data){
                console.error(data.data);
                $location.path('/panel/');
            }
        }

        function createSimulation(){
            Round.createSimulation(vm.roundName).then(createSimulationSuccessFn, createSimulationErrorFn);

            function createSimulationSuccessFn(){
                $.jGrowl("Simulation has been created successfully.", {
                    life: 2500,
                    theme: 'success'
                });
                $route.reload();
            }

            function createSimulationErrorFn(data){
                console.error(data.data);
                $.jGrowl("Simulation can't be created.", {
                    life: 2500,
                    theme: 'btn-danger'
                });
                $route.reload();
            }
        }

        function associateAgent(){
            var agent_name = document.getElementById("select").value;
            console.log(vm.identifier);

            Round.getSimulationAgents(vm.identifier).then(getSimulationAgentsSuccessFn, getSimulationAgentsErrorFn);

            function getSimulationAgentsSuccessFn(data) {
                vm.simulationAgents = data.data;
                vm.simulationAgents.count = vm.simulationAgents.length +1;

                console.log(vm.roundName + ' ' + vm.identifier + ' ' + agent_name + ' ' + vm.simulationAgents.count);

                Round.associateAgent(vm.roundName, vm.identifier, agent_name, vm.simulationAgents.count).then(associateAgentSuccessFn, associateAgentErrorFn);

                function associateAgentSuccessFn(){
                    $.jGrowl("Agent has been associated successfully.", {
                        life: 2500,
                        theme: 'success'
                    });
                    $route.reload();
                }

                function associateAgentErrorFn(data){
                    console.error(data.data);
                    $.jGrowl("Agent can't be associated.", {
                        life: 2500,
                        theme: 'btn-danger'
                    });
                    $route.reload();
                }
            }

            function getSimulationAgentsErrorFn(data) {
                console.error(data.data);
                $location.path('/panel/');
            }



        }

        function uploadParamList() {
            var selectedFile = document.getElementById('ParamListUpload').files[0];

            console.log(selectedFile);
            Round.uploadParamList(vm.roundName, selectedFile).then(uploadSuccessFn, uploadErrorFn);

            function uploadSuccessFn(){

                $.jGrowl("File \'" + selectedFile.name + "\' has been uploaded.", {
                    life: 2500,
                    theme: 'success'
                });
            }

            function uploadErrorFn(data){
                $.jGrowl("File \'" + selectedFile.name + "\' can't be uploaded.", {
                    life: 2500,
                    theme: 'btn-danger'
                });
                console.log(data.data);
            }

        }

        function uploadGrid() {
            var selectedFile = document.getElementById('GridUpload').files[0];

            Round.uploadGrid(vm.roundName, selectedFile).then(uploadSuccessFn, uploadErrorFn);

            function uploadSuccessFn(){

                $.jGrowl("File \'" + selectedFile.name + "\' has been uploaded.", {
                    life: 2500,
                    theme: 'success'
                });
            }

            function uploadErrorFn(data){
                $.jGrowl("File \'" + selectedFile.name + "\' can't be uploaded.", {
                    life: 2500,
                    theme: 'btn-danger'
                });
                console.log(data.data);
            }

        }

        function uploadLab() {
            var selectedFile = document.getElementById('LabUpload').files[0];

            Round.uploadLab(vm.roundName, selectedFile).then(uploadSuccessFn, uploadErrorFn);

            function uploadSuccessFn(){

                $.jGrowl("File \'" + selectedFile.name + "\' has been uploaded.", {
                    life: 2500,
                    theme: 'success'
                });
            }

            function uploadErrorFn(data){
                $.jGrowl("File \'" + selectedFile.name + "\' can't be uploaded.", {
                    life: 2500,
                    theme: 'btn-danger'
                });
                console.log(data.data);
            }

        }

    }

})();

