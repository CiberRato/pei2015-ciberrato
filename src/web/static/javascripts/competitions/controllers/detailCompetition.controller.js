(function(){

    'use strict';

    angular
        .module('ciberonline.competitions.controllers')
        .controller('DetailCompetitionController', DetailCompetitionController);

    DetailCompetitionController.$inject = ['$location', '$timeout', '$routeParams', 'Competition', 'Team', 'Authentication', 'Round'];

    function DetailCompetitionController($location, $timeout, $routeParams, Competition, Team, Authentication, Round){
        var vm = this;
        var competitionName = $routeParams.name;
        var authenticatedAccount = Authentication.getAuthenticatedAccount();

        vm.username = authenticatedAccount.username;

        vm.enroll = enroll;
        vm.removeInscription = removeInscription;
        vm.change_page = change_page;

        activate();

        function activate(){

            Competition.getCompetition(competitionName).then(getCompetitionSuccessFn, getCompetitionErrorFn);
            Team.getUserAdmin(vm.username).then(getUserAdminSuccessFn, getUserAdminErrorFn);
            Competition.getAllRounds(competitionName).then(getAllRoundsSuccessFn, getAllRoundsErrorFn);

            function getCompetitionSuccessFn(data){
                vm.competition = data.data;
            }

            function getCompetitionErrorFn(data){
                console.error(data.data);
                $location.url('/panel/');
            }

            function getUserAdminSuccessFn(data){
                vm.userAdmin = data.data;
                Competition.getTeams(competitionName).then(getTeamsSuccessFn, getTeamsErrorFn);

                function getTeamsSuccessFn(data) {
                    vm.competitionTeamsInfo = data.data;
                    Competition.getMyTeams(vm.username, competitionName).then(getMyTeamsSuccessFn, getMyTeamsErrorFn);

                    var confirm;
                    var k = 0;
                    vm.teamsToShow = [];
                    vm.myTeams = [];
                    for (var i = 0; i < vm.userAdmin.length; i++) {
                        confirm = false;
                        for (var j = 0; j < vm.competitionTeamsInfo.length; j++) {
                            if (vm.userAdmin[i].name === vm.competitionTeamsInfo[j].group.name) {
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
                        if(vm.myTeams[j].group_name === vm.competitionTeamsInfo[i].group.name){
                            vm.competitionTeamsInfo[i].show=true;
                        }
                    }
                }

                console.log(vm.competitionTeamsInfo);

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
            }

            function getTrials(roundName, i){
                Round.getTrials(roundName).then(getTrialsSuccessFn, getTrialsErrorFn);

                function getTrialsSuccessFn(data){
                    vm.rounds[i].simulations = data.data;
                }

                function getTrialsErrorFn(data){
                    console.error(data.data);
                    $location.path('/panel/');

                }
            }

            function getAllRoundsErrorFn(data){
                console.error(data.data);
                $location.path('/panel/');
            }

        }

        function enroll(){
            var x = document.getElementById("select").value;
            Competition.enroll(competitionName,x).then(enrollSuccessFn, enrollErrorFn);

            function enrollSuccessFn(){
                $.jGrowl("Team has been joined to the competition.", {
                    life: 2500,
                    theme: 'success'
                });
                $timeout(function(){
                    getTeams();
                });
            }

            function enrollErrorFn(data){
                console.error(data.data);
                $.jGrowl(data.data.message, {
                    life: 2500,
                    theme: 'btn-danger'
                });
            }
        }



        function removeInscription(teamName){
            Competition.deleteEnroll(teamName, competitionName).then(deleteEnrollSuccessFn, deleteEnrollErrorFn);

            function deleteEnrollSuccessFn(){
                $.jGrowl("Team has been removed from the competition.", {
                    life: 2500,
                    theme: 'success'
                });
                $timeout(function(){
                    getTeams();
                });

            }

            function deleteEnrollErrorFn(){
                $.jGrowl(data.data.message, {
                    life: 2500,
                    theme: 'btn-danger'
                });
                $location.path('/panel/competitions/'+ competitionName + '/');
            }

        }

        function change_page(){
            $location.path('/panel/' + vm.username + '/createTeam')
        }

        function getTeams(){
            Team.getUserAdmin(vm.username).then(getUserAdminSuccessFn, getUserAdminErrorFn);
            function getUserAdminSuccessFn(data){
                vm.userAdmin = data.data;
                Competition.getTeams(competitionName).then(getTeamsSuccessFn, getTeamsErrorFn);

                function getTeamsSuccessFn(data) {
                    vm.competitionTeamsInfo = data.data;
                    Competition.getMyTeams(vm.username, competitionName).then(getMyTeamsSuccessFn, getMyTeamsErrorFn);

                    var confirm;
                    var k = 0;
                    vm.teamsToShow = [];
                    vm.myTeams = [];
                    for (var i = 0; i < vm.userAdmin.length; i++) {
                        confirm = false;
                        for (var j = 0; j < vm.competitionTeamsInfo.length; j++) {
                            if (vm.userAdmin[i].name === vm.competitionTeamsInfo[j].group.name) {
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
                        if(vm.myTeams[j].group_name === vm.competitionTeamsInfo[i].group.name){
                            vm.competitionTeamsInfo[i].show=true;
                        }
                    }
                }

                console.log(vm.competitionTeamsInfo);

            }

            function getMyTeamsErrorFn(data){
                console.error(data.data);
                $location.url('/panel/');

            }
        }


    }



})();
