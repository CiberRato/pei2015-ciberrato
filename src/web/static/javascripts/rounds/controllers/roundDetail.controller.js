(function(){

    'use strict';

    angular
        .module('ciberonline.rounds.controllers')
        .controller('DetailRoundController', DetailRoundController);

    DetailRoundController.$inject = ['$location', '$route', '$routeParams', 'Round', 'Competition'];

    function DetailRoundController($location, $route, $routeParams, Round, Competition){
        var vm = this;

        vm.models = {
            selected: null,
            lists: {"Available": [], "Simulation": []}
        };

        console.log(vm.models);

        vm.createSimulation = createSimulation;
        vm.moved = moved;
        vm.identifier;
        vm.roundName = $routeParams.name;
        vm.uploadParamList = uploadParamList;
        vm.uploadGrid = uploadGrid;
        vm.uploadLab = uploadLab;
        vm.destroy = destroy;
        vm.removeSimulation = removeSimulation;
        vm.uploadAll = uploadAll;
        vm.reload = reload;
        vm.getSimulationGrids = getSimulationGrids;
        vm.Available = [];
        vm.disassociateGrid = disassociateGrid;
        vm.startSimulation = startSimulation;
        vm.all = false;
        activate();

        function activate() {
            Round.getSimulations(vm.roundName).then(getSimulationsSuccessFn, getSimulationsErrorFn);
            Round.getRound(vm.roundName).then(getRoundSuccessFn, getRoundErrorFn);
            Round.getFiles(vm.roundName).then(getRoundFilesSuccessFn, getRoundFilesErrorFn);


            function getSimulationsSuccessFn(data) {
                vm.simulations = data.data;
                for (var i= 0; i<vm.simulations.length; i++){
                    getSimulationGrids(vm.simulations[i], i);
                }
            }

            function getSimulationGrids(simulation, i){
                Round.getSimulationGrids(simulation.identifier).then(getSimulationGridsSuccessFn, getSimulationGridsErrorFn);

                function getSimulationGridsSuccessFn(data){
                    console.log(data.data);
                    vm.models.lists.Simulation = [];
                    for (var k = 0; k < data.data.length; ++k) {
                        vm.models.lists.Simulation.push({label: data.data[k].grid_positions.group_name, identifier: data.data[k].grid_positions.identifier, position: data.data[k].position});
                    }
                    console.log(vm.models.lists.Simulation);
                    vm.simulations[i].gridsTotal= vm.models.lists.Simulation;
                    console.log(vm.simulations[i].gridsTotal.length);
                }

                function getSimulationGridsErrorFn(data){
                    console.error(data.data);
                    $location.path('/panel/');
                }
            }

            function getSimulationsErrorFn(data) {
                console.error(data.data);
                $location.path('/panel/');
            }


            function getRoundSuccessFn(data){
                vm.round = data.data;
                Round.getGrids(vm.round.parent_competition_name).then(getGridsFirstSuccessFn, getGridsFirstErrorFn);

                function getGridsFirstSuccessFn(data){
                    for (var i = 0; i < data.data.length; ++i) {
                        vm.Available.push({label: data.data[i].group_name, identifier: data.data[i].identifier});
                    }
                    Competition.getCompetition(vm.round.parent_competition_name).then(getCompetitionSuccessFn, getCompetitionErrorFn);

                    function getCompetitionSuccessFn(data){
                        vm.competition = data.data;
                        console.log(vm.competition);
                    }

                    function getCompetitionErrorFn(data){
                        console.error(data.data);
                        $location.path('/panel/');
                    }
                }

                function getGridsFirstErrorFn(data){
                    console.error(data.data);
                    $location.path('/panel/');
                }
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
                console.log(vm.files);
            }

            function getRoundFilesErrorFn(data){
                console.error(data.data);
                $location.path('/panel/');
            }


        }

        function moved(group_name ,identifier){
            console.log(isInSimulation(group_name, identifier));
            if(isInSimulation(group_name)) {
                associateGrid(identifier);
            }
        }

        function isInSimulation(group_name){
            for (var i=0; i<vm.models.lists.Available.length; i++){
                if (vm.models.lists.Available[i].label===group_name){
                    return false;
                }
            }
            return true;
        }

        function isInSimulationNew(group_name){
            for (var i=0; i<vm.models.lists.Simulation.length; i++){
                if (vm.models.lists.Simulation[i].label===group_name){
                    return true;
                }
                console.log(vm.models.lists.Simulation[i].label)
            }
            return false;
        }

        function getGridsSuccessFn(data) {
            console.log(data.data);
            vm.models.lists.Available=[];
            for (var i = 0; i < data.data.length; ++i) {
                if(isInSimulationNew(data.data[i].group_name) === false){

                    vm.models.lists.Available.push({
                        label: data.data[i].group_name,
                        identifier: data.data[i].identifier
                    });

                }
            }
            console.log(vm.models.lists.Available);
            console.log(vm.models.lists.Simulation);
        }

        function getGridsErrorFn(data) {
            console.error(data.data);
            $location.path('/panel/');
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
                $.jGrowl(data.data.message, {
                    life: 2500,
                    theme: 'btn-danger'
                });
                $route.reload();
            }
        }

        function associateGrid(grid_identifier) {
            console.log(vm.identifier);

            Round.getSimulationGrids(vm.identifier).then(getSimulationAgentsSuccessFn, getSimulationAgentsErrorFn);

            function getSimulationAgentsSuccessFn(data) {
                var pos = data.data.length + 1;
                console.log(pos);

                Round.associateGrid(grid_identifier, vm.identifier, pos).then(associateAgentSuccessFn, associateAgentErrorFn);

                function associateAgentSuccessFn() {
                    $.jGrowl("Grid has been associated successfully.", {
                        life: 2500,
                        theme: 'success'
                    });
                    getSimulationGrids();

                }

                function associateAgentErrorFn(data) {
                    console.error(data.data);
                    $.jGrowl(data.data.message, {
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

        function disassociateGrid(pos) {
            Round.disassociateAgent(vm.identifier, pos).then(disassociateAgentSuccessFn, disassociateAgentErrorFn);

            function disassociateAgentSuccessFn() {

                $.jGrowl("Agent has been disassociated successfully.", {
                    life: 2500,
                    theme: 'success'
                });
                getSimulationGrids();
            }

            function disassociateAgentErrorFn(data) {
                console.error(data.data);
                $.jGrowl(data.data.message, {
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

                if(vm.all === true){
                    var selectedFile2 = document.getElementById('GridUpload').files[0];
                    var selectedFile3 = document.getElementById('LabUpload').files[0];

                    if(selectedFile2 != undefined){
                        uploadGrid();
                        console.log('fizgrd');
                    }else if(selectedFile3 != undefined){
                        uploadLab();
                    }else{
                        $route.reload();
                        $('.modal-backdrop').remove();
                        vm.all = false;
                    }

                }
            }

            function uploadErrorFn(data){
                console.log(data.data);
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
                $.jGrowl(errors, {
                    life: 5000,
                    theme: 'btn-danger'
                });
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

                if(vm.all === true){
                    var selectedFile3 = document.getElementById('LabUpload').files[0];
                    if(selectedFile3 != undefined){
                        uploadLab();
                        console.log('fizlab');
                    }else{
                        $route.reload();
                        $('.modal-backdrop').remove();
                        vm.all = false;
                    }

                }
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
                if(vm.all === true){
                    $route.reload();
                    $('.modal-backdrop').remove();
                    vm.all = false;
                }

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
            vm.all = true;
            console.log(vm.all);
            var selectedFile1 = document.getElementById('ParamListUpload').files[0];

            if(selectedFile1 != undefined){
                uploadParamList();
                console.log('fizparam');
            }else{
                uploadGrid();
            }
        }

        function reload(){
            $route.reload();
            $('.modal-backdrop').remove();

        }

        function getSimulationGrids(){
            Round.getSimulationGrids(vm.identifier).then(getSimulationGridsSuccessFn, getSimulationGridsErrorFn);

            function getSimulationGridsSuccessFn(data){
                console.log(data.data);
                vm.models.lists.Simulation = [];
                for (var i = 0; i < data.data.length; ++i) {
                    vm.models.lists.Simulation.push({label: data.data[i].grid_positions.group_name, identifier: data.data[i].grid_positions.identifier, position: data.data[i].position});
                }
                console.log(vm.models.lists.Simulation);
                Round.getGrids(vm.round.parent_competition_name).then(getGridsSuccessFn, getGridsErrorFn);

            }

            function getSimulationGridsErrorFn(data){
                console.error(data.data);
                $location.path('/panel/');
            }
        }

        function startSimulation(identifier){
            console.log(identifier);
            Round.startSimulation(identifier).then(startSimulationSuccessFn, startSimulationErrorFn);

            function startSimulationSuccessFn(){
                $.jGrowl("Simulation has been started successfully.", {
                    life: 2500,
                    theme: 'success'
                });
                $route.reload();
            }

            function startSimulationErrorFn(){
                $.jGrowl("Simulation can't be started.", {
                    life: 2500,
                    theme: 'btn-danger'
                });
                $route.reload();
            }

        }

        function saveScores(){
            for(var i = 0; i<vm.models.lists.Simulation; i++){
                var inputText = document.getElementById("teamsTrial"+vm.models.lists.Simulation[i].label).value;

            }

        }


    }

})();

