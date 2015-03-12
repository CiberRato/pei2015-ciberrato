(function(){

    'use strict';

    angular
        .module('ciberonline.competitions.controllers')
        .controller('DetailCompetitionController', DetailCompetitionController);

    DetailCompetitionController.$inject = ['$location', '$routeParams', 'Competition', 'Team', 'Authentication'];

    function DetailCompetitionController($location, $routeParams, Competition, Team, Authentication){
        var vm = this;
        var competitionName = $routeParams.name;
        vm.enroll = enroll;

        activate();

        function activate(){
            var authenticatedAccount = Authentication.getAuthenticatedAccount();
            var username = authenticatedAccount.username;
            Competition.getCompetition(competitionName).then(getCompetitionSuccessFn, getCompetitionErrorFn);
            Competition.getNotValidTeams(competitionName).then(getNotValidTeamsSuccessFn, getNotValidTeamsErrorFn);
            Team.getByUser(username).then(getTeamsByUserSuccessFn, getTeamsByUserErrorFn);


            function getCompetitionSuccessFn(data, status, headers, config){
                vm.competition = data.data;
            }

            function getCompetitionErrorFn(data, status, headers, config){
                console.error(data.data);
                $location.url('/panel/');
            }

            function getNotValidTeamsSuccessFn(data, status, headers, config){
                vm.competitionNotValidTeamsInfo = data.data;
            }

            function getNotValidTeamsErrorFn(data, status, headers, config){
                console.error(data.data);
                $location.url('/panel/');
            }

            function getTeamsByUserSuccessFn(data, status, headers, config){
                vm.myTeams = data.data;
                console.log(vm.myTeams);
                /*for(var i = 0; i< vm.myTeams.length;i++){
                    if(vm.myTeams[i] in vm.competition){
                        vm.myTeams[i].();
                    }
                }*/
                console.log(vm.myTeams);
            }


            function getTeamsByUserErrorFn(data, status, headers, config){
                console.error(data.data);
            }

        }

        function enroll(){
            var x = document.getElementById("select").value;
            console.log(x);
            Competition.enroll(competitionName,x).then(enrollSuccessFn, enrollErrorFn);
        }

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

})();
