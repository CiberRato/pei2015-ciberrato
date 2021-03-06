(function(){

    'use strict';

    angular
        .module('ciberonline.competitions.controllers')
        .controller('ListCompetitionController', ListCompetitionController);

    ListCompetitionController.$inject = ['$location', '$timeout', '$routeParams', 'Competition', 'Round', '$scope', 'Team', 'Authentication', 'Grid', 'Agent', 'Notification'];

    function ListCompetitionController($location, $timeout, $routeParams, Competition, Round, $scope, Team, Authentication, Grid, Agent, Notification){
        var vm = this;
        vm.competitionName = $routeParams.name;
        vm.validateInscription = validateInscription;
        vm.getGrids = getGrids;
        vm.getScoresByTrial = getScoresByTrial;
        vm.getScoresByRound = getScoresByRound;
        vm.getScoresByCompetition = getScoresByCompetition;
        vm.identifier;
        vm.removeInscription = removeInscription;
        vm.getGrid = getGrid;
        vm.models = {
            selected: null,
            lists: {"Available": [], "GridPosition": []}
        };
        vm.associateAllRemote=associateAllRemote;
        vm.associate = associate;
        vm.disassociate = disassociate;
        var authenticatedAccount = Authentication.getAuthenticatedAccount();

        vm.username = authenticatedAccount.username;
        var subscribed = false;

        activate();

        function activate() {
            $scope.loader = {
                loading: false
            };

            if(!subscribed){
                subscribed = true;
                var round_notification = Notification.events.subscribe('notificationbroadcast', 1, function(data){
                    console.log(data);

                    if (data.message.trigger == 'trial_prepare' || data.message.trigger == 'trial_error' || data.message.trigger == 'trial_log' || data.message.trigger == 'trial_start'){
                        $timeout(function () {
                            activate();
                        });
                    }

                    console.log(data._type);
                    console.log(data.message);
                });
                console.log(round_notification);
                $scope.$on("$destroy", function(event){
                    round_notification.remove();
                });
            }

            Competition.getCompetition(vm.competitionName).then(getCompetitionSuccessFn, getCompetitionErrorFn);

            function getCompetitionSuccessFn(data){
                vm.competition = data.data;
                console.log(vm.competition);
                Team.getUserAdmin(vm.username).then(getUserAdminSuccessFn, getUserAdminErrorFn);

            }

            function getCompetitionErrorFn(data){
                console.error(data.data);
                $location.path('/panel/');
            }

            function getUserAdminSuccessFn(data){
                vm.userAdmin = data.data;
                Competition.getTeams(vm.competitionName).then(getTeamsSuccessFn, getTeamsErrorFn);

                function getTeamsSuccessFn(data) {
                    vm.competitionTeamsInfo = data.data;
                    Competition.getMyTeams(vm.username, vm.competitionName).then(getMyTeamsSuccessFn, getMyTeamsErrorFn);

                    var confirm;
                    var k = 0;
                    vm.teamsToShow = [];
                    vm.myTeams = [];
                    for (var i = 0; i < vm.userAdmin.length; i++) {
                        confirm = false;
                        for (var j = 0; j < vm.competitionTeamsInfo.length; j++) {
                            if (vm.userAdmin[i].name === vm.competitionTeamsInfo[j].team.name) {
                                confirm = true;
                                vm.competitionTeamsInfo[j].canRemove = true;
                            }
                        }
                        if (confirm === false) {
                            vm.teamsToShow[k] = vm.userAdmin[i];
                            k++;
                        }
                    }

                }

                function getTeamsErrorFn(data) {
                    console.error(data.data);
                    $location.url('/panel/');
                }


            }
            function getUserAdminErrorFn(data){
                console.error(data.data);
            }

            function getMyTeamsSuccessFn(data){
                vm.myTeams = data.data;
                for(var i = 0; i<vm.competitionTeamsInfo.length; i++){
                    vm.competitionTeamsInfo[i].show=false;
                    for(var j =0; j<vm.myTeams.length; j++){
                        if(vm.myTeams[j].team_name === vm.competitionTeamsInfo[i].team.name){
                            vm.competitionTeamsInfo[i].show=true;
                        }
                    }
                }

                console.log(vm.competitionTeamsInfo);
                Competition.getAllRounds(vm.competitionName).then(getAllRoundsSuccessFn, getAllRoundsErrorFn);

            }

            function getMyTeamsErrorFn(data){
                console.error(data.data);
                $location.url('/panel/');

            }

            function getAllRoundsSuccessFn(data){
                vm.rounds = data.data;
                for(var i = 0; i<vm.rounds.length; i++){
                    getTrials(vm.rounds[i].name, i);
                }
                $scope.loader = {
                    loading: true
                };
            }

            function getTrials(roundName, i){
                Round.getTrials(roundName, vm.competitionName).then(getTrialsSuccessFn, getTrialsErrorFn);

                function getTrialsSuccessFn(data){
                    vm.rounds[i].trials = data.data;
                    for(var j = 0; j<vm.rounds[i].trials.length; j++){
                        getGrids(vm.rounds[i].trials[j].identifier, j, i);
                    }
                }

                function getTrialsErrorFn(data){
                    console.error(data.data);
                    $location.path('/panel/');

                }
            }

            function getGrids(trialIdentifier, k, i){
                Round.getTrialGrids(trialIdentifier, k, i).then(getTrialGridsSuccessFn, getTrialGridsErrorFn);

                function getTrialGridsSuccessFn(data){
                    vm.rounds[i].trials[k].grids = data.data;
                    console.log(vm.rounds[i].trials[k]);

                }

                function getTrialGridsErrorFn(data){
                    console.error(data.data);
                    $location.path('/panel/');
                }
            }

            function getAllRoundsErrorFn(data){
                console.error(data.data);
                $location.path('/panel/');
            }
        }


        function validateInscription(team_name, competition_name){
            Competition.validateInscription(team_name, competition_name).then(validateInscriptionSuccessFn, validateInscriptionErrorFn);

            function validateInscriptionSuccessFn(){
                $timeout(function(){
                    Competition.getTeams(vm.competitionName).then(getTeamsSuccessFn, getTeamsErrorFn);

                    function getTeamsSuccessFn(data) {
                        vm.competitionTeamsInfo = data.data;
                    }

                    function getTeamsErrorFn(data) {
                        console.error(data.data);
                        $location.url('/panel/');
                    }
                });
            }
            function validateInscriptionErrorFn(data){
                console.error(data.data);
                $location.path('/admin/');
            }

        }

        function getGrids(identifier){
            Round.getTrialGrids(identifier).then(getTrialGridsSuccessFn, getTrialGridsErrorFn);

            function getTrialGridsSuccessFn(data){
                vm.grids = data.data;
                console.log(vm.grids);

            }

            function getTrialGridsErrorFn(data){
                console.error(data.data);
                $location.path('/panel/');
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

        function getScoresByRound(name, competitionName){
            Round.getScoresByRound(name, competitionName).then(getScoresByRoundSuccessFn, getScoresByRoundErrorFn);

            function getScoresByRoundSuccessFn(data){
                vm.scoresByRound = data.data;
            }

            function getScoresByRoundErrorFn(data){
                console.error(data.data);
            }
        }

        function getScoresByCompetition(){
            Competition.getScoresByCompetition(vm.competitionName).then(getScoresByCompetitionSuccessFn, getScoresByCompetitionErrorFn);

            function getScoresByCompetitionSuccessFn(data){
                vm.scoresByCompetition = data.data;
            }

            function getScoresByCompetitionErrorFn(data){
                console.error(data.data);
            }
        }

        function removeInscription(teamName){
            console.log(teamName);
            Competition.deleteEnroll(teamName, vm.competition.name).then(deleteEnrollSuccessFn, deleteEnrollErrorFn);

            function deleteEnrollSuccessFn(){
                $.jGrowl("Team has been removed from the competition.", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                });
                $timeout(function(){
                    Competition.getTeams(vm.competitionName).then(getTeamsSuccessFn, getTeamsErrorFn);

                    function getTeamsSuccessFn(data) {
                        vm.competitionTeamsInfo = data.data;
                    }

                    function getTeamsErrorFn(data) {
                        console.error(data.data);
                        $location.url('/panel/');
                    }
                });

            }

            function deleteEnrollErrorFn(data){
                $.jGrowl(data.data.message, {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
                });
            }

        }

        function getGrid(teamName, competitionName){
            vm.tmp1 = false;
            Grid.getGrid(teamName, competitionName).then(success, error);

            function success(data){
                console.log(data.data);
                vm.grid = data.data;
                Agent.getValidByTeam(teamName).then(getByTeamSuccessFn, getByTeamErrorFn);

            }

            function error(data){
                console.error(data.data);
            }
        }

        function getByTeamSuccessFn(data) {
            vm.models.lists.Available = [];
            for (var i = 0; i < data.data.length; ++i) {
                if(data.data[i].agent_name === "Remote" && vm.competition.type_of_competition.allow_remote_agents === true){
                    vm.models.lists.Available.push({label: data.data[i].agent_name, type: 'Available'});
                }else if(data.data[i].agent_name !== "Remote"){
                    vm.models.lists.Available.push({label: data.data[i].agent_name, type: 'Available'});
                }
            }
            if(vm.models.lists.Available.length == 0){
                vm.tmp1 = true;
            }
            console.log(vm.grid.identifier);
            Grid.getAgents(vm.grid.identifier).then(getAssociatedSuccessFn, getAssociatedErrorFn);
        }

        function getByTeamErrorFn(data){
            console.error(data.data);
            $location.url('/panel/');

        }

        function getAssociatedSuccessFn(data){
            vm.models.lists.GridPosition = [];
            for (var i = 0; i < data.data.length; ++i) {
                vm.models.lists.GridPosition.push({label: data.data[i].agent_name, pos: data.data[i].position, type: 'Grid'});
            }
        }

        function getAssociatedErrorFn(data){
            console.error(data.data);
            $location.url('/panel/');

        }

        function associate(agent_name, teamName){
            console.log(vm.models.lists);

            var pos = vm.models.lists.GridPosition.length;
            console.log(teamName);
            Grid.associateAgent(agent_name, vm.grid.identifier, pos, teamName).then(associateSuccessFn, associateErrorFn);

            function associateSuccessFn(){
                $.jGrowl("Agent has been associated successfully.", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                });
                Grid.getAgents(vm.grid.identifier).then(getAssociatedSuccessFn, getAssociatedErrorFn);
                Agent.getValidByTeam(teamName).then(getByTeamSuccessFn, getByTeamErrorFn);

            }

            function associateErrorFn(data){
                console.error(data.data);
            }

        }

        function disassociate(pos, teamName) {
            Grid.disassociateAgent(vm.grid.identifier, pos, teamName).then(disassociateSuccessFn, disassociateErrorFn);
            console.log(vm.models.lists.GridPosition);
            function disassociateSuccessFn() {
                $.jGrowl("Agent has been disassociated successfully.", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                });

                Agent.getValidByTeam(teamName).then(getByTeamSuccessFn, getByTeamErrorFn);

                function getByTeamSuccessFn(data) {
                    vm.models.lists.Available = [];
                    for (var i = 0; i < data.data.length; ++i) {
                        if(data.data[i].agent_name === "Remote" && vm.competition.type_of_competition.allow_remote_agents === true){
                            vm.models.lists.Available.push({label: data.data[i].agent_name, type: 'Available'});
                        }else if(data.data[i].agent_name !== "Remote"){
                            vm.models.lists.Available.push({label: data.data[i].agent_name, type: 'Available'});
                        }
                    }
                    console.log(vm.models.lists.Available);
                    Grid.getAgents(vm.grid.identifier).then(getAssociatedAgentsSuccessFn, getAssociatedAgentsErrorFn);


                }

                function getByTeamErrorFn(data) {
                    console.error(data.data);
                    $location.url('/panel/');

                }

            }

            function disassociateErrorFn(data) {
                console.error(data.data);
                $.jGrowl(data.data.message, {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
                });
            }

            function getAssociatedAgentsSuccessFn(data) {
                vm.models.lists.GridPosition = [];
                for (var i = 0; i < data.data.length; ++i) {
                    vm.models.lists.GridPosition.push({label: data.data[i].agent_name, pos: data.data[i].position});
                }
                console.log(vm.models.lists.GridPosition);
                if (vm.models.lists.GridPosition !== []) {
                    for (var j = 0; j < vm.models.lists.GridPosition.length; j++) {
                        gridDisassociate(vm.models.lists.GridPosition[j].pos);
                    }
                    vm.tmp = vm.models.lists.GridPosition;
                    Grid.getAgents(vm.grid.identifier).then(getAssociatedNSuccessFn, getAssociatedNErrorFn);

                }

                function getAssociatedNSuccessFn() {
                    console.log(vm.models.lists.GridPosition);
                    for (var k = 0; k < vm.tmp.length; k++) {
                        gridAssociate(vm.tmp[k].label, k + 1, teamName);
                    }
                    console.log(vm.models.lists.GridPosition);
                    Grid.getAgents(vm.grid.identifier).then(getAssociatedSuccessFn, getAssociatedErrorFn);
                }

                function getAssociatedNErrorFn(data) {
                    console.error(data.data);
                }

            }

            function getAssociatedAgentsErrorFn(data) {
                console.error(data.data);
                $location.url('/panel/');

            }
        }

        function gridDisassociate(pos){
            Grid.disassociateAgent(vm.grid.identifier, pos).then(disassociateSuccessFn, disassociateErrorFn);

            function disassociateSuccessFn(){
                console.log("desassociei" + pos);
            }

            function disassociateErrorFn(data){
                console.error(data.data);
            }
        }

        function gridAssociate(agent_name, pos, teamName){
            Grid.associateAgent(agent_name, vm.grid.identifier, pos, teamName).then(associateAgentSuccessFn, associateAgentErrorFn);

            function associateAgentSuccessFn(){
                console.log("associei" + agent_name + pos);

                Grid.getAgents(vm.grid.identifier).then(getAssociatedSuccessFn, getAssociatedErrorFn);
                Agent.getValidByTeam(teamName).then(getByTeamSuccessFn, getByTeamErrorFn);

            }

            function associateAgentErrorFn(data){
                console.error(data.data);
            }
        }

        function associateAllRemote(){
            console.log(vm.models.lists.GridPosition.length);
            for(var i = vm.models.lists.GridPosition.length; i<vm.competition.type_of_competition.number_agents_by_grid; i++){
                associateRemote(i+1);
            }
        }

        function associateRemote(i){
            Grid.associateAgent("Remote", vm.grid.identifier, i, vm.grid.team_name).then(associateAgentSuccessFn, associateAgentErrorFn);

            function associateAgentSuccessFn(){
                $.jGrowl("Agent has been associated successfully.", {
                    life: 2500,
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
                });
                Grid.getAgents(vm.grid.identifier).then(getAssociatedSuccessFn, getAssociatedErrorFn);
                Agent.getValidByTeam(vm.grid.team_name).then(getByTeamSuccessFn, getByTeamErrorFn);

            }

            function associateAgentErrorFn(data){
                console.error(data.data);
            }

        }




    }

})();
