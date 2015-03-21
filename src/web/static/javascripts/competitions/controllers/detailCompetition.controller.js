(function(){

    'use strict';

    angular
        .module('ciberonline.competitions.controllers')
        .controller('DetailCompetitionController', DetailCompetitionController);

    DetailCompetitionController.$inject = ['$location', '$route', '$routeParams', 'Competition', 'Team', 'Authentication'];

    function DetailCompetitionController($location, $route, $routeParams, Competition, Team, Authentication){
        var vm = this;
        var competitionName = $routeParams.name;
        var authenticatedAccount = Authentication.getAuthenticatedAccount();

        vm.username = authenticatedAccount.username;

        vm.enroll = enroll;
        vm.removeInscription = removeInscription;
        vm.change_page = change_page;
        vm.validateInscription = validateInscription;

        activate();

        function activate(){

            Competition.getCompetition(competitionName).then(getCompetitionSuccessFn, getCompetitionErrorFn);
            Team.getUserAdmin(vm.username).then(getUserAdminSuccessFn, getUserAdminErrorFn);

            function getCompetitionSuccessFn(data, status, headers, config){
                vm.competition = data.data;
            }

            function getCompetitionErrorFn(data, status, headers, config){
                console.error(data.data);
                $location.url('/panel/');
            }

            function getUserAdminSuccessFn(data, status, headers, config){
                vm.userAdmin = data.data;
                Competition.getTeams(competitionName).then(getTeamsSuccessFn, getTeamsErrorFn);

                function getTeamsSuccessFn(data, status, headers, config) {
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

                function getTeamsErrorFn(data, status, headers, config) {
                    console.error(data.data);
                    $location.url('/panel/');
                }


            }
            function getUserAdminErrorFn(data, status, headers, config){
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

        function enroll(){
            var x = document.getElementById("select").value;
            Competition.enroll(competitionName,x).then(enrollSuccessFn, enrollErrorFn);

            function enrollSuccessFn(data, status, headers, config){
                $.jGrowl("Team has been joined to the competition.", {
                    life: 2500,
                    theme: 'success'
                });
                $location.path('/panel/competitions/'+ competitionName + '/');
            }

            function enrollErrorFn(data, status, headers, config){
                console.error(data.data);
                $.jGrowl("Team could not join the competition.", {
                    life: 2500,
                    theme: 'btn-danger'
                });
            }
        }



        function removeInscription(teamName){
            Competition.deleteEnroll(teamName, competitionName).then(deleteEnrollSuccessFn, deleteEnrollErrorFn);

            function deleteEnrollSuccessFn(data, status, headers, config){
                $.jGrowl("Team has been removed from the competition.", {
                    life: 2500,
                    theme: 'success'
                });
                $location.path('/panel/competitions/'+ competitionName + '/');
            }

            function deleteEnrollErrorFn(data, status, headers, config){
                $.jGrowl("Team can't be removed from the competition.", {
                    life: 2500,
                    theme: 'btn-danger'
                });
                $location.path('/panel/competitions/'+ competitionName + '/');
            }

        }

        function change_page(){
            $location.path('/panel/' + vm.username + '/createTeam')
        }

        function validateInscription(group_name, competition_name){
            Competition.validateInscription(group_name, competition_name).then(validateInscriptionSuccessFn, validateInscriptionErrorFn);

            function validateInscriptionSuccessFn(){
                console.log('deu');
                $route.reload();            }
            function validateInscriptionErrorFn(data){
                console.error(data.data);
                $location.path('/admin/');
            }

        }

    }

})();
