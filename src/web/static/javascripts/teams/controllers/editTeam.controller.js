(function () {
    'use strict';

    angular
        .module('ciberonline.teams.controllers')
        .controller('EditTeamController', EditTeamController);

    EditTeamController.$inject = ['$location', '$routeParams', 'Authentication', 'Team'];

    function EditTeamController($location, $routeParams, Authentication, Team){
        var vm = this;
        var username;
        var teamName;
        vm.update = update;

        activate();

        function activate(){
            teamName = $routeParams.name;

            Team.getTeam(teamName).then(getTeamSuccessFn, getTeamErrorFn);

            function getTeamSuccessFn(data, status, headers, config){
                vm.team = data.data;
            }

            function getTeamErrorFn(data, status, headers, config){
                $location.url('/');
            }
        }

        function update(){
            Team.update(vm.team, teamName).then(updateTeamSuccessFn, updateTeamErrorFn);

            function updateTeamSuccessFn(data, status, headers, config){
                $location.path("/panel/" + username + "/myTeams");
            }

            function updateTeamErrorFn(data, status, headers, config){

            }
        }
    }
})();

