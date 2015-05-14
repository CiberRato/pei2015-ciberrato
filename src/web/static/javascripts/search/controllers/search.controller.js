(function(){
    'use strict';

    angular
        .module('ciberonline.search.controllers')
        .controller('SearchController', SearchController);

    SearchController.$inject = ['$location', '$routeParams','Team', 'Profile', 'Competition', '$scope'];

    function SearchController($location, $routeParams, Team, Profile, Competition, $scope){
        var vm = this;
        var search = $routeParams.search;

        activate();

        function activate(){
            $scope.loader = {
                loading: false
            };
            Team.getAll().then(getAllSuccessFn, getAllErrorFn);


            function getAllSuccessFn(data){
                vm.team = data.data;
                var j = 0;
                vm.teamsFound = [];
                console.log(vm.team);
                for(var i = 0; i<vm.team.length; i++){
                    if(vm.team[i].name === search){
                        vm.teamsFound[j] = vm.team[i];
                        j++;
                    }
                }
                Profile.getAll().then(getAllMembersSuccessFn, getAllMembersErrorFn);
            }

            function getAllErrorFn(data){
                console.error(data.data);
                $location.path('/panel/');
            }

            function getAllMembersSuccessFn(data){
                vm.members = data.data;
                var j = 0;
                console.log(vm.members);
                vm.membersFound =[];
                for(var i = 0; i<vm.members.length; i++) {
                    if (vm.members[i].username === search || (vm.members[i].first_name === search.substr(0,search.indexOf(' ')) && vm.members[i].last_name === search.substr(search.indexOf(' ')+1)) || vm.members[i].first_name === search || vm.members[i].last_name === search){
                        vm.membersFound[j] = vm.members[i];
                        j++;
                    }
                }
                Competition.getAll().then(getAllCompetitionsSuccessFn, getAllCompetitionsErrorFn);

            }

            function getAllMembersErrorFn(data){
                console.error(data.data);
                $location.path('/panel/');
            }

            function getAllCompetitionsSuccessFn(data){
                vm.competitions = data.data;
                var j = 0;
                vm.competitionsFound = [];
                for(var i = 0; i<vm.competitions.length; i++){
                    if(vm.competitions[i].name === search){
                        vm.competitionsFound[j] = vm.competitions[i];
                        j++;
                    }
                }
                $scope.loader = {
                    loading: true
                };
            }

            function getAllCompetitionsErrorFn(data){
                console.error(data.data);
                $location.path('/panel/');
            }
        }
    }
})();