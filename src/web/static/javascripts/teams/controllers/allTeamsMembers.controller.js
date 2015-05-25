(function(){
    'use strict';

    angular
        .module('ciberonline.teams.controllers')
        .controller('AllTeamsMembersController', AllTeamsMembersController);

    AllTeamsMembersController.$inject = ['$location', '$routeParams','Team', '$scope'];

    function AllTeamsMembersController($location, $routeParams, Team, $scope){
        var vm = this;
        var teamName;
        activate();

        function activate(){
            $scope.loader = {
                loading: false
            };

            teamName = $routeParams.name;

            Team.getMembers(teamName).then(getMembersSuccessFn, getMembersErrorFn);

            function getMembersSuccessFn(data){
                vm.members = data.data;
                vm.team = teamName;
                $scope.loader = {
                    loading: true
                };
            }

            function getMembersErrorFn(data){
                console.error(data.data);
                $location.path('/panel/');
            }
        }
    }
})();

