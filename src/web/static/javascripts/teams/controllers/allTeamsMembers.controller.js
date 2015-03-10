(function(){
    'use strict';

    angular
        .module('ciberonline.teams.controllers')
        .controller('AllTeamsMembersController', AllTeamsMembersController);

    AllTeamsMembersController.$inject = ['$location', '$routeParams','Team'];

    function AllTeamsMembersController($location, $routeParams, Team){
        var vm = this;
        var teamName;
        activate();

        function activate(){
            teamName = $routeParams.name;

            Team.getMembers(teamName).then(getMembersSuccessFn, getMembersErrorFn);

            function getMembersSuccessFn(data, status, headers, config){
                vm.members = data.data;
                vm.team = teamName;
            }

            function getMembersErrorFn(data, status, headers, config){
                console.error(data.data);
                $location.path('/panel/');
            }
        }
    }
})();

