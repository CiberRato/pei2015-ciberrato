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
            lists: {"Available": [], "Trial": []}
        };

        vm.competitionName = $routeParams.competitionName;
        vm.createTrial = createTrial;
        vm.moved = moved;
        vm.identifier;
        vm.roundName = $routeParams.name;
        vm.uploadParamList = uploadParamList;
        vm.uploadGrid = uploadGrid;
        vm.uploadLab = uploadLab;
        vm.destroy = destroy;
        vm.removeTrial = removeTrial;
        vm.uploadAll = uploadAll;

        vm.getTrialGrids = getTrialGrids;
        vm.Available = [];
        vm.disassociateGrid = disassociateGrid;
        vm.startTrial = startTrial;
        vm.all = false;
        vm.getScoresByTrial = getScoresByTrial;
        activate();

        function activate() {
            Round.getTrials(vm.roundName, vm.competitionName).then(getTrialsSuccessFn, getTrialsErrorFn);
            Round.getRound(vm.roundName, vm.competitionName).then(getRoundSuccessFn, getRoundErrorFn);
            Round.getFiles(vm.roundName).then(getRoundFilesSuccessFn, getRoundFilesErrorFn);


            function getTrialsSuccessFn(data) {
                vm.trials = data.data;
                console.log(vm.trials);
                for (var i= 0; i<vm.trials.length; i++){
                    getTrialGridsFirst(vm.trials[i], i);
                }
            }

            function getTrialGridsFirst(trial, i){
                Round.getTrialGrids(trial.identifier).then(getTrialGridsFirstSuccessFn, getTrialGridsFirstErrorFn);

                function getTrialGridsFirstSuccessFn(data){
                    vm.models.lists.Trial = [];
                    for (var k = 0; k < data.data.length; ++k) {
                        vm.models.lists.Trial.push({label: data.data[k].grid_positions.team_name, identifier: data.data[k].grid_positions.identifier, position: data.data[k].position});
                    }
                    vm.trials[i].gridsTotal= vm.models.lists.Trial;
                }

                function getTrialGridsFirstErrorFn(data){
                    console.error(data.data);
                    $location.path('/panel/');
                }
            }

            function getTrialsErrorFn(data) {
                console.error(data.data);
                $location.path('/panel/');
            }


            function getRoundSuccessFn(data){
                vm.round = data.data;
                Round.getGrids(vm.round.parent_competition_name).then(getGridsFirstSuccessFn, getGridsFirstErrorFn);

                function getGridsFirstSuccessFn(data){
                    for (var i = 0; i < data.data.length; ++i) {
                        vm.Available.push({label: data.data[i].team_name, identifier: data.data[i].identifier});
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
            }

            function getRoundFilesErrorFn(data){
                console.error(data.data);
                $location.path('/panel/');
            }


        }

        function moved(team_name ,identifier){
            if(isInTrial(team_name)) {
                associateGrid(identifier);
            }
        }

        function isInTrial(team_name){
            for (var i=0; i<vm.models.lists.Available.length; i++){
                if (vm.models.lists.Available[i].label===team_name){
                    return false;
                }
            }
            return true;
        }

        function isInTrialNew(team_name){
            for (var i=0; i<vm.models.lists.Trial.length; i++){
                if (vm.models.lists.Trial[i].label===team_name){
                    return true;
                }
            }
            return false;
        }

        function getGridsSuccessFn(data) {
            vm.models.lists.Available=[];
            for (var i = 0; i < data.data.length; ++i) {
                if(isInTrialNew(data.data[i].team_name) === false){

                    vm.models.lists.Available.push({
                        label: data.data[i].team_name,
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


        function createTrial(){
            Round.createTrial(vm.roundName, vm.competitionName).then(createTrialSuccessFn, createTrialErrorFn);

            function createTrialSuccessFn(){
                $.jGrowl("Trial has been created successfully.", {
                    life: 2500,
                    theme: 'success'
                });
                $timeout(function(){
                    reloadTrials();
                });
            }

            function createTrialErrorFn(data){
                console.error(data.data);
                $.jGrowl(data.data.message, {
                    life: 2500,
                    theme: 'btn-danger'
                });
                $timeout(function(){
                    reloadTrials();
                });
            }
        }

        function associateGrid(grid_identifier) {

            Round.getTrialGrids(vm.identifier).then(getTrialAgentsSuccessFn, getTrialAgentsErrorFn);

            function getTrialAgentsSuccessFn(data) {
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

            function getTrialAgentsErrorFn(data) {
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

                Round.getTrialGrids(vm.identifier).then(getTrialGridsNSuccessFn, getTrialGridsNErrorFn);

                function getTrialGridsNSuccessFn(data){
                    vm.models.lists.Trial = [];
                    for (var i = 0; i < data.data.length; ++i) {
                        vm.models.lists.Trial.push({label: data.data[i].grid_positions.team_name, identifier: data.data[i].grid_positions.identifier, position: data.data[i].position});
                    }

                    if(vm.models.lists.Trial !== []){
                        for(var j = 0; j<vm.models.lists.Trial.length; j++){
                            disassociate(vm.models.lists.Trial[j].position);
                        }
                        Round.getTrialGrids(vm.identifier).then(getSuccessFn, getErrorFn);

                    }

                    function getSuccessFn(data){
                        vm.Trial=[];
                        for (var i = 0; i < data.data.length; ++i) {
                            vm.Trial.push({label: data.data[i].grid_positions.team_name, identifier: data.data[i].grid_positions.identifier, position: data.data[i].position});
                        }

                        for(var k= 0; k<vm.models.lists.Trial.length; k++){
                            gridAssociate(vm.models.lists.Trial[k].identifier, k+1);
                        }
                        Round.getGrids(vm.round.parent_competition_name).then(getGridsSuccessFn, getGridsErrorFn);

                    }

                    function getErrorFn(data){
                        console.error(data.data);
                    }

                }

                function getTrialGridsNErrorFn(data){
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

            Round.uploadParamList(vm.roundName, selectedFile, vm.competitionName).then(uploadSuccessFn, uploadErrorFn);

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

            Round.uploadGrid(vm.roundName, selectedFile, vm.competitionName).then(uploadSuccessFn, uploadErrorFn);

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

            Round.uploadLab(vm.roundName, selectedFile, vm.competitionName).then(uploadSuccessFn, uploadErrorFn);

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
            Round.destroy(vm.roundName, vm.competitionName).then(destroySuccessFn, destroyErrorFn);

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

        function removeTrial(identifier){
            Round.removeTrial(identifier).then(removeTrialSuccessFn, removeTrialErrorFn);

            function removeTrialSuccessFn(){
                $.jGrowl("Trial has been removed.", {
                    life: 2500,
                    theme: 'success'
                });

                $timeout(function(){
                    reloadTrials();
                });

            }

            function removeTrialErrorFn(data){
                $.jGrowl("Trial can't be removed.", {
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

        function getTrialGrids(){
            Round.getTrialGrids(vm.identifier).then(getTrialGridsSuccessFn, getTrialGridsErrorFn);

        }

        function getTrialGridsSuccessFn(data){
            vm.models.lists.Trial = [];
            for (var i = 0; i < data.data.length; ++i) {
                vm.models.lists.Trial.push({label: data.data[i].grid_positions.team_name, identifier: data.data[i].grid_positions.identifier, position: data.data[i].position});
            }
            Round.getGrids(vm.round.parent_competition_name).then(getGridsSuccessFn, getGridsErrorFn);

        }

        function getTrialGridsErrorFn(data){
            console.error(data.data);
            $location.path('/panel/');
        }

        function startTrial(identifier){
            Round.startTrial(identifier).then(startTrialSuccessFn, startTrialErrorFn);

            function startTrialSuccessFn(){
                $.jGrowl("Trial has been started successfully.", {
                    life: 2500,
                    theme: 'success'
                });
                $timeout(function(){
                    reloadTrial(identifier);
                });
            }

            function startTrialErrorFn(data){
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

        function reloadTrial(identifier){
            setTimeout(function () {
                $timeout(function(){
                    Round.getTrial(identifier).then(getTrialSuccessFn, getTrialErrorFn);
                });
            }, 1000);


            function getTrialSuccessFn(data){
                if (!(data.data.state === 'READY')) {
                    vm.trial = data.data;
                    updateState(identifier);
                }
            }

            function getTrialErrorFn(data){
                console.error(data.data);
            }

        }

        function updateState(identifier){
            for(var i =0; i<vm.trials.length; i++){
                if(vm.trial.identifier === vm.trials[i].identifier){
                    if(vm.trial.state !== vm.trials[i].state){
                        vm.trials[i].state = vm.trial.state;
                        console.log(vm.trials[i].state);
                    }
                }
            }

            setTimeout(function () {
                Round.getTrial(identifier).then(getTrialNSuccessFn, getTrialErrorFn);
            }, 1000);

            function getTrialNSuccessFn(data){
                if (!(data.data.state === 'READY')) {
                    vm.trial = data.data;
                    if(vm.trial.state === 'LOG' || vm.trial.state === 'ERROR'){
                        updateState2(identifier);
                    }else{
                        updateState(identifier);

                    }
                }
            }

            function getTrialErrorFn(data){
                console.error(data.data);
            }
        }

        function updateState2(identifier) {
            for (var i = 0; i < vm.trials.length; i++) {
                if (vm.trial.identifier === vm.trials[i].identifier) {
                    if (vm.trial.state !== vm.trials[i].state) {
                        vm.trials[i].state = vm.trial.state;
                        console.log(vm.trials[i].state);
                    }
                }
            }

            setTimeout(function () {
                Round.getTrial(identifier).then(getTrialNSuccessFn, getTrialErrorFn);
            }, 5000);

            function getTrialNSuccessFn(data) {
                if (!(data.data.state === 'READY' || data.data.state === 'LOG' || data.data.state === 'ERROR')) {
                    vm.trial = data.data;
                    updateState2(identifier);
                }
            }

            function getTrialErrorFn(data) {
                console.error(data.data);
            }
        }

        function gridAssociate(grid, pos){
            Round.associateGrid(grid, vm.identifier, pos).then(associateAgentSuccessFn, associateAgentErrorFn);

            function associateAgentSuccessFn(){
                Round.getTrialGrids(vm.identifier).then(getNewTrialGridsSuccessFn, getNewTrialGridsErrorFn);

                function getNewTrialGridsSuccessFn(data){
                    vm.models.lists.Trial = [];
                    for (var k = 0; k < data.data.length; ++k) {
                        vm.models.lists.Trial.push({label: data.data[k].grid_positions.team_name, identifier: data.data[k].grid_positions.identifier, position: data.data[k].position});
                    }
                }

                function getNewTrialGridsErrorFn(data){
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
            console.log(vm.models.lists.Trial);
            for(var i=0; i< vm.models.lists.Trial.length; i++){
                var score = document.getElementById("score"+vm.models.lists.Trial[i].label).value;
                var agents = document.getElementById("agents"+vm.models.lists.Trial[i].label).value;
                var time = document.getElementById("time"+vm.models.lists.Trial[i].label).value;

                var exists = false;
                for(var k=0; k<vm.scoresByTrial.length; k++){
                    if(vm.models.lists.Trial[i].label === vm.scoresByTrial[k].team.name){
                        exists = true;
                        vm.team = vm.scoresByTrial[k];
                    }
                }
                console.log(score + " " + agents + " " + time);

                console.log(exists);
                if(exists === true){
                    updateScore(score, agents, time, vm.models.lists.Trial[i].label, vm.team);
                }
                else if((score !== "" && agents !== "" && time !=="") && exists === false){
                    saveScore(score, agents, time, vm.models.lists.Trial[i].label);
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

        function reloadTrials(){
            Round.getTrials(vm.roundName).then(getTrialsSuccessFn, getTrialsErrorFn);

            function getTrialsSuccessFn(data) {
                vm.trials = data.data;
                console.log(vm.trials);
                for (var i= 0; i<vm.trials.length; i++){
                    getTrialGridsFirst(vm.trials[i], i);
                }
            }

            function getTrialGridsFirst(trial, i){
                Round.getTrialGrids(trial.identifier).then(getTrialGridsFirstSuccessFn, getTrialGridsFirstErrorFn);

                function getTrialGridsFirstSuccessFn(data){
                    vm.models.lists.Trial = [];
                    for (var k = 0; k < data.data.length; ++k) {
                        vm.models.lists.Trial.push({label: data.data[k].grid_positions.team_name, identifier: data.data[k].grid_positions.identifier, position: data.data[k].position});
                    }
                    vm.trials[i].gridsTotal= vm.models.lists.Trial;
                }

                function getTrialGridsFirstErrorFn(data){
                    console.error(data.data);
                    $location.path('/panel/');
                }
            }

            function getTrialsErrorFn(data) {
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
            Round.getTrialGrids(vm.identifier).then(getTrialGridsFirstSuccessFn, getTrialGridsFirstErrorFn);

            function getTrialGridsFirstSuccessFn(data){
                vm.models.lists.Trial = [];
                for (var k = 0; k < data.data.length; ++k) {
                    vm.models.lists.Trial.push({label: data.data[k].grid_positions.team_name, identifier: data.data[k].grid_positions.identifier, position: data.data[k].position});
                }

                for(var i = 0; i<vm.trials.length; i++){
                    if(vm.identifier === vm.trials[i].identifier){
                        vm.trials[i].gridsTotal= vm.models.lists.Trial;
                    }
                }

            }

            function getTrialGridsFirstErrorFn(data){
                console.error(data.data);
                $location.path('/panel/');
            }

        }


    }

})();

