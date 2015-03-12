(function(){
    'use strict';

    angular
        .module('ciberonline.search.controllers')
        .controller('SearchController', SearchController);

    SearchController.$inject = ['$location', '$routeParams','Team', 'Profile'];

    function SearchController($location, $routeParams, Team, Profile){
        var vm = this;
        var search = $routeParams.search;

        activate();

        function activate(){
            Team.getAll().then(getAllSuccessFn, getAllErrorFn);
            Profile.getAll().then(getAllMembersSuccessFn, getAllMembersErrorFn);

            function getAllSuccessFn(data, status, headers, config){
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
                console.log(vm.teamsFound);
                vm.teamsFound.count = vm.teamsFound.length;
            }

            function getAllErrorFn(data, status, headers, config){
                console.error(data.data);
                $location.path('/panel/');
            }

            function getAllMembersSuccessFn(data, status, headers, config){
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
                console.log(vm.membersFound);
                vm.membersFound.count = vm.membersFound.length;
            }

            function getAllMembersErrorFn(data, status, headers, config){
                console.error(data.data);
                $location.path('/panel/');
            }
        }
    }
})();