(function(){

    'use strict';

    angular
        .module('ciberonline.rounds.controllers')
        .controller('DetailRoundController', DetailRoundController);

    DetailRoundController.$inject = ['$location', '$route', '$timeout', '$scope', '$routeParams', 'Round', 'Competition'];

    function DetailRoundController($location, $route, $timeout, $scope, $routeParams, Round, Competition){
        var vm = this;

        vm.saveScores = saveScores;

        vm.models = {
            selected: null,
            lists: {"Available": [], "Simulation": []}
        };


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

        vm.getSimulationGrids = getSimulationGrids;
        vm.Available = [];
        vm.disassociateGrid = disassociateGrid;
        vm.startSimulation = startSimulation;
        vm.all = false;
        vm.getScoresByTrial = getScoresByTrial;
        activate();

        function activate() {
            Round.getSimulations(vm.roundName).then(getSimulationsSuccessFn, getSimulationsErrorFn);
            Round.getRound(vm.roundName).then(getRoundSuccessFn, getRoundErrorFn);
            Round.getFiles(vm.roundName).then(getRoundFilesSuccessFn, getRoundFilesErrorFn);


            function getSimulationsSuccessFn(data) {
                vm.simulations = data.data;
                console.log(vm.simulations);
                for (var i= 0; i<vm.simulations.length; i++){
                    getSimulationGridsFirst(vm.simulations[i], i);
                }
            }

            function getSimulationGridsFirst(simulation, i){
                Round.getSimulationGrids(simulation.identifier).then(getSimulationGridsFirstSuccessFn, getSimulationGridsFirstErrorFn);

                function getSimulationGridsFirstSuccessFn(data){
                    vm.models.lists.Simulation = [];
                    for (var k = 0; k < data.data.length; ++k) {
                        vm.models.lists.Simulation.push({label: data.data[k].grid_positions.group_name, identifier: data.data[k].grid_positions.identifier, position: data.data[k].position});
                    }
                    vm.simulations[i].gridsTotal= vm.models.lists.Simulation;
                }

                function getSimulationGridsFirstErrorFn(data){
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
            }

            function getRoundFilesErrorFn(data){
                console.error(data.data);
                $location.path('/panel/');
            }


        }

        function moved(group_name ,identifier){
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
            }
            return false;
        }

        function getGridsSuccessFn(data) {
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
            $timeout(function(){
                reloadGridsTotal();
            });

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
                $timeout(function(){
                    reloadSimulations();
                });
            }

            function createSimulationErrorFn(data){
                console.error(data.data);
                $.jGrowl(data.data.message, {
                    life: 2500,
                    theme: 'btn-danger'
                });
                $timeout(function(){
                    reloadSimulations();
                });
            }
        }

        function associateGrid(grid_identifier) {

            Round.getSimulationGrids(vm.identifier).then(getSimulationAgentsSuccessFn, getSimulationAgentsErrorFn);

            function getSimulationAgentsSuccessFn(data) {
                var pos = data.data.length + 1;

                Round.associateGrid(grid_identifier, vm.identifier, pos).then(associateAgentSuccessFn, associateAgentErrorFn);

                function associateAgentSuccessFn() {
                    $.jGrowl("Grid has been associated successfully.", {
                        life: 2500,
                        theme: 'success'
                    });

                    $timeout(function(){
                        reloadGridsTotal();
                    });

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

                $.jGrowl("Grid has been disassociated successfully.", {
                    life: 2500,
                    theme: 'success'
                });

                Round.getSimulationGrids(vm.identifier).then(getSimulationGridsNSuccessFn, getSimulationGridsNErrorFn);

                function getSimulationGridsNSuccessFn(data){
                    vm.models.lists.Simulation = [];
                    for (var i = 0; i < data.data.length; ++i) {
                        vm.models.lists.Simulation.push({label: data.data[i].grid_positions.group_name, identifier: data.data[i].grid_positions.identifier, position: data.data[i].position});
                    }

                    if(vm.models.lists.Simulation !== []){
                        for(var j = 0; j<vm.models.lists.Simulation.length; j++){
                            disassociate(vm.models.lists.Simulation[j].position);
                        }
                        Round.getSimulationGrids(vm.identifier).then(getSuccessFn, getErrorFn);

                    }

                    function getSuccessFn(data){
                        vm.Simulation=[];
                        for (var i = 0; i < data.data.length; ++i) {
                            vm.Simulation.push({label: data.data[i].grid_positions.group_name, identifier: data.data[i].grid_positions.identifier, position: data.data[i].position});
                        }

                        for(var k= 0; k<vm.models.lists.Simulation.length; k++){
                            gridAssociate(vm.models.lists.Simulation[k].identifier, k+1);
                        }
                        Round.getGrids(vm.round.parent_competition_name).then(getGridsSuccessFn, getGridsErrorFn);

                    }

                    function getErrorFn(data){
                        console.error(data.data);
                    }

                }

                function getSimulationGridsNErrorFn(data){
                    console.error(data.data);
                    $location.path('/panel/');
                }

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
                    }else if(selectedFile3 != undefined){
                        uploadLab();
                    }else{
                        $timeout(function(){
                            getFiles();
                        });
                        $('.modal-backdrop').remove();
                        vm.all = false;
                    }

                }else {
                    $timeout(function () {
                        getFiles();
                    });
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
                    }else{
                        $timeout(function(){
                            getFiles();
                        });
                        $('.modal-backdrop').remove();
                        vm.all = false;
                    }

                }else {
                    $timeout(function () {
                        getFiles();
                    });
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
                    $timeout(function(){
                        getFiles();
                    });
                    $('.modal-backdrop').remove();
                    vm.all = false;
                }else{
                    $timeout(function(){
                        getFiles();
                    });
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

                $timeout(function(){
                    reloadSimulations();
                });

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
            var selectedFile1 = document.getElementById('ParamListUpload').files[0];

            if(selectedFile1 != undefined){
                uploadParamList();
            }else{
                uploadGrid();
            }
        }

        function getSimulationGrids(){
            Round.getSimulationGrids(vm.identifier).then(getSimulationGridsSuccessFn, getSimulationGridsErrorFn);

        }

        function getSimulationGridsSuccessFn(data){
            vm.models.lists.Simulation = [];
            for (var i = 0; i < data.data.length; ++i) {
                vm.models.lists.Simulation.push({label: data.data[i].grid_positions.group_name, identifier: data.data[i].grid_positions.identifier, position: data.data[i].position});
            }
            Round.getGrids(vm.round.parent_competition_name).then(getGridsSuccessFn, getGridsErrorFn);

        }

        function getSimulationGridsErrorFn(data){
            console.error(data.data);
            $location.path('/panel/');
        }

        function startSimulation(identifier){
            Round.startSimulation(identifier).then(startSimulationSuccessFn, startSimulationErrorFn);

            function startSimulationSuccessFn(){
                $.jGrowl("Simulation has been started successfully.", {
                    life: 2500,
                    theme: 'success'
                });
                $timeout(function(){
                    reloadSimulations();
                });
            }

            function startSimulationErrorFn(data){
                console.log(data.data);
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

        function gridAssociate(grid, pos){
            Round.associateGrid(grid, vm.identifier, pos).then(associateAgentSuccessFn, associateAgentErrorFn);

            function associateAgentSuccessFn(){
                Round.getSimulationGrids(vm.identifier).then(getNewSimulationGridsSuccessFn, getNewSimulationGridsErrorFn);

                function getNewSimulationGridsSuccessFn(data){
                    vm.models.lists.Simulation = [];
                    for (var k = 0; k < data.data.length; ++k) {
                        vm.models.lists.Simulation.push({label: data.data[k].grid_positions.group_name, identifier: data.data[k].grid_positions.identifier, position: data.data[k].position});
                    }
                }

                function getNewSimulationGridsErrorFn(data){
                    console.error(data.data);
                }
            }

            function associateAgentErrorFn(data){
                console.error(data.data);
            }
        }

        function disassociate(pos){
            Round.disassociateAgent(vm.identifier, pos).then(disassociateSuccessFn, disassociateErrorFn);

            function disassociateSuccessFn(){

            }

            function disassociateErrorFn(data){
                console.error(data.data);
            }
        }

        function saveScores(){
            console.log(vm.models.lists.Simulation);
            for(var i=0; i< vm.models.lists.Simulation.length; i++){
                var score = document.getElementById("score"+vm.models.lists.Simulation[i].label).value;
                var agents = document.getElementById("agents"+vm.models.lists.Simulation[i].label).value;
                var time = document.getElementById("time"+vm.models.lists.Simulation[i].label).value;

                var exists = false;
                for(var k=0; k<vm.scoresByTrial.length; k++){
                    if(vm.models.lists.Simulation[i].label === vm.scoresByTrial[k].team.name){
                        exists = true;
                        vm.team = vm.scoresByTrial[k];
                    }
                }
                console.log(score + " " + agents + " " + time);

                console.log(exists);
                if(exists === true){
                    updateScore(score, agents, time, vm.models.lists.Simulation[i].label, vm.team);
                }
                else if((score !== "" && agents !== "" && time !=="") && exists === false){
                    saveScore(score, agents, time, vm.models.lists.Simulation[i].label);
                }else{
                    $.jGrowl("Scores can't be created successfully. Please fill all fields", {
                        life: 2500,
                        theme: 'btn-danger'
                    });
                }
            }
        }

        function saveScore(score, agents, time, team){
            Round.saveScore(vm.identifier, team, score, agents, time).then(saveScoreSuccessFn, saveScoreErrorFn);

            function saveScoreSuccessFn(){
                $.jGrowl("Scores has been created successfully.", {
                    life: 2500,
                    theme: 'success'
                });
                $timeout(function(){
                    getScoresByTrial();
                });
            }

            function saveScoreErrorFn(data){
                console.error(data.data);


            }
        }

        function updateScore(score, agents, time, team, teamDetail){
            if(score === ""){
                score = teamDetail.score;
            }
            if(agents === ""){
                agents = teamDetail.number_of_agents;
            }
            if(time === ""){
                time = teamDetail.time;
            }

            Round.updateScore(vm.identifier, team, score, agents, time).then(updateScoreSuccessFn, updateScoreErrorFn);

            function updateScoreSuccessFn(){
                $.jGrowl("Scores has been updated successfully.", {
                    life: 2500,
                    theme: 'success'
                });
                $timeout(function(){
                    getScoresByTrial();
                });
            }

            function updateScoreErrorFn(data){
                console.error(data.data);
            }
        }

        function getScoresByTrial(){
            Round.getScoresByTrial(vm.identifier).then(getScoresByTrialSuccessFn, getScoresByTrialErrorFn);

            function getScoresByTrialSuccessFn(data){
                vm.scoresByTrial = data.data;
                console.log(vm.scoresByTrial);
            }

            function getScoresByTrialErrorFn(data){
                console.error(data.data);
            }


        }

        function reloadSimulations(){
            Round.getSimulations(vm.roundName).then(getSimulationsSuccessFn, getSimulationsErrorFn);

            function getSimulationsSuccessFn(data) {
                vm.simulations = data.data;
                console.log(vm.simulations);
                for (var i= 0; i<vm.simulations.length; i++){
                    getSimulationGridsFirst(vm.simulations[i], i);
                }
            }

            function getSimulationGridsFirst(simulation, i){
                Round.getSimulationGrids(simulation.identifier).then(getSimulationGridsFirstSuccessFn, getSimulationGridsFirstErrorFn);

                function getSimulationGridsFirstSuccessFn(data){
                    vm.models.lists.Simulation = [];
                    for (var k = 0; k < data.data.length; ++k) {
                        vm.models.lists.Simulation.push({label: data.data[k].grid_positions.group_name, identifier: data.data[k].grid_positions.identifier, position: data.data[k].position});
                    }
                    vm.simulations[i].gridsTotal= vm.models.lists.Simulation;
                }

                function getSimulationGridsFirstErrorFn(data){
                    console.error(data.data);
                    $location.path('/panel/');
                }
            }

            function getSimulationsErrorFn(data) {
                console.error(data.data);
                $location.path('/panel/');
            }
        }

        function getFiles(){
            Round.getFiles(vm.roundName).then(getRoundFilesSuccessFn, getRoundFilesErrorFn);

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

        function reloadGridsTotal(){
            Round.getSimulationGrids(vm.identifier).then(getSimulationGridsFirstSuccessFn, getSimulationGridsFirstErrorFn);

            function getSimulationGridsFirstSuccessFn(data){
                vm.models.lists.Simulation = [];
                for (var k = 0; k < data.data.length; ++k) {
                    vm.models.lists.Simulation.push({label: data.data[k].grid_positions.group_name, identifier: data.data[k].grid_positions.identifier, position: data.data[k].position});
                }

                for(var i = 0; i<vm.simulations.length; i++){
                    if(vm.identifier === vm.simulations[i].identifier){
                        vm.simulations[i].gridsTotal= vm.models.lists.Simulation;
                    }
                }

            }

            function getSimulationGridsFirstErrorFn(data){
                console.error(data.data);
                $location.path('/panel/');
            }

        }


    }

})();

