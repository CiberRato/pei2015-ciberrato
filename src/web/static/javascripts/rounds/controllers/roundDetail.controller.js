(function(){

    'use strict';

    angular
        .module('ciberonline.rounds.controllers')
        .controller('DetailRoundController', DetailRoundController);

    DetailRoundController.$inject = ['$location', '$route', '$routeParams', 'Round', 'StreamViewer'];

    function DetailRoundController($location, $route, $routeParams, Round, StreamViewer){
        var vm = this;

        vm.models = {
            selected: null,
            lists: {"Available": [], "Simulation": []}
        };

        console.log(vm.models);

        vm.createSimulation = createSimulation;
        vm.moved = moved;
        vm.getSimulationAgents = getSimulationAgents;
        vm.identifier;
        vm.roundName = $routeParams.name;
        vm.uploadParamList = uploadParamList;
        vm.uploadGrid = uploadGrid;
        vm.uploadLab = uploadLab;
        vm.destroy = destroy;
        vm.removeSimulation = removeSimulation;
        vm.uploadAll = uploadAll;
        vm.reload = reload;
        activate();

        function activate() {
            Round.getSimulations(vm.roundName).then(getSimulationsSuccessFn, getSimulationsErrorFn);
            Round.getAgents(vm.roundName).then(getAgentsSuccessFn, getAgentsErrorFn);
            Round.getRound(vm.roundName).then(getRoundSuccessFn, getRoundErrorFn);
            Round.getFiles(vm.roundName).then(getRoundFilesSuccessFn, getRoundFilesErrorFn);

            function getSimulationsSuccessFn(data) {
                vm.simulations = data.data;
                for (var i= 0; i<vm.simulations.length; i++){

                }
            }

            function getSimulationsErrorFn(data) {
                console.error(data.data);
                $location.path('/panel/');
            }

            function getAgentsSuccessFn(data) {
                for (var i = 0; i < data.data.length; ++i) {
                    vm.models.lists.Available.push({label: data.data[i].agent_name});
                }
            }

            function getAgentsErrorFn(data) {
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

            function getRoundFilesSuccessFn(data){
                vm.files = data.data;
                vm.grid = vm.files.grid;
                vm.lab = vm.files.lab;
                vm.param_list = vm.files.param_list;
            }

            function getRoundFilesErrorFn(data){
                console.error(data.data);
                $location.path('/panel/');
            }
        }

        function getSimulationAgents(){
            Round.getSimulationAgents(vm.identifier).then(getSimulationAgentsSuccessFn, getSimulationAgentsErrorFn);

            function getSimulationAgentsSuccessFn(data) {
                vm.models.lists.Simulation = [];
                for (var i = 0; i < data.data.length; ++i) {
                    vm.models.lists.Simulation.push({label: data.data[i].agent_name});
                }
            }

            function getSimulationAgentsErrorFn(data) {
                console.error(data.data);
                //$location.path('/panel/');
            }
        }

        function moved(agent_name){
            console.log(isInSimulation(agent_name));
            if(isInSimulation(agent_name)){
                associateAgent(agent_name);
            }else{
                disassociateAgent(agent_name);
            }
        }

        function isInSimulation(agent_name){
            for (var i=0; i<vm.models.lists.Available.length; i++){
                if (vm.models.lists.Available[i].label===agent_name){
                    return false;
                }
            }
            return true;
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

        function associateAgent(agent_name) {
            console.log(vm.identifier);

            Round.getSimulationAgents(vm.identifier).then(getSimulationAgentsSuccessFn, getSimulationAgentsErrorFn);

            function getSimulationAgentsSuccessFn(data) {
                var pos = data.data.length + 1;

                Round.associateAgent(vm.roundName, vm.identifier, agent_name, pos).then(associateAgentSuccessFn, associateAgentErrorFn);

                function associateAgentSuccessFn() {
                    $.jGrowl("Agent has been associated successfully.", {
                        life: 2500,
                        theme: 'success'
                    });
                }

                function associateAgentErrorFn(data) {
                    console.error(data.data);
                    $.jGrowl("Agent can't be associated.", {
                        life: 2500,
                        theme: 'btn-danger'
                    });
                }
            }

            function getSimulationAgentsErrorFn(data) {
                console.error(data.data);
                $location.path('/panel/');
            }
        }

        function disassociateAgent(agent_name) {

            Round.disassociateAgent(vm.roundName, vm.identifier, agent_name).then(disassociateAgentSuccessFn, disassociateAgentErrorFn);

            function disassociateAgentSuccessFn() {
                $.jGrowl("Agent has been disassociated successfully.", {
                    life: 2500,
                    theme: 'success'
                });
            }

            function disassociateAgentErrorFn(data) {
                console.error(data.data);
                $.jGrowl("Agent can't be disassociated!.", {
                    life: 2500,
                    theme: 'btn-danger'
                });
            }
        }

        function uploadParamList() {
            var selectedFile = document.getElementById('ParamListUpload').files[0];

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
                console.error(data.data);
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
                console.error(data.data);
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
                console.error(data.data);
            }

        }

        function destroy(){
            Round.destroy(vm.roundName).then(destroySuccessFn, destroyErrorFn);

            function destroySuccessFn(){
                $.jGrowl("Round has been removed.", {
                    life: 2500,
                    theme: 'success'
                });
                $location.path('/admin/' + vm.round.parent_competition_name);
            }

            function destroyErrorFn(data){
                $.jGrowl("Round can't be removed.", {
                    life: 2500,
                    theme: 'btn-danger'
                });
                console.error(data.data);
                $route.reload();
            }
        }

        function removeSimulation(identifier){
            Round.removeSimulation(identifier).then(removeSimulationSuccessFn, removeSimulationErrorFn);

            function removeSimulationSuccessFn(){
                $.jGrowl("Simulation has been removed.", {
                    life: 2500,
                    theme: 'success'
                });
                $route.reload();
            }

            function removeSimulationErrorFn(data){
                $.jGrowl("Simulation can't be removed.", {
                    life: 2500,
                    theme: 'btn-danger'
                });
                console.error(data.data);
            }
        }

        function uploadAll(){
            var selectedFile1 = document.getElementById('ParamListUpload').files[0];
            console.log(selectedFile1);
            var selectedFile2 = document.getElementById('GridUpload').files[0];
            console.log(selectedFile2);
            var selectedFile3 = document.getElementById('LabUpload').files[0];
            console.log(selectedFile3);
            if(selectedFile1 != undefined){
                uploadParamList();
            }
            if(selectedFile2 != undefined){
                uploadGrid();
            }
            if(selectedFile3 != undefined){
                uploadLab();
            }

            $route.reload();
            $('.modal-backdrop').remove();
        }

        function reload(){
            $route.reload();
            $('.modal-backdrop').remove();

        }

    }

})();

