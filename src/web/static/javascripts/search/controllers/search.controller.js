(function(){
    'use strict';

    angular
        .module('ciberonline.search.controllers')
        .controller('SearchController', SearchController);

    SearchController.$inject = ['$location', '$routeParams','Team', 'Profile', 'Competition', '$scope'];

    function SearchController($location, $routeParams, Team, Profile, Competition, $scope){
        var vm = this;
        var search = $routeParams.search;
        vm.changeUsers = changeUsers;
        vm.change = change;

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
                for(var i = 0; i<vm.team.results.length; i++){
                    if(vm.team.results[i].name === search){
                        vm.teamsFound[j] = vm.team.results[i];
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
                for(var i = 0; i<vm.members.results.length; i++) {
                    if (vm.members.results[i].username === search || (vm.members.results[i].first_name === search.substr(0,search.indexOf(' ')) && vm.members.results[i].last_name === search.substr(search.indexOf(' ')+1)) || vm.members.results[i].first_name === search || vm.members.results[i].last_name === search){
                        vm.membersFound[j] = vm.members.results[i];
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
                console.log(vm.competitions);
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

        function changeUsers(url){
            Profile.change(url).then(changeSuccessFn, changeErrorFn);

            function changeSuccessFn(data){
                vm.members = data.data;
                var j = 0;
                console.log(vm.members);
                vm.membersFound =[];
                for(var i = 0; i<vm.members.results.length; i++) {
                    if (vm.members.results[i].username === search || (vm.members.results[i].first_name === search.substr(0,search.indexOf(' ')) && vm.members.results[i].last_name === search.substr(search.indexOf(' ')+1)) || vm.members.results[i].first_name === search || vm.members.results[i].last_name === search){
                        vm.membersFound[j] = vm.members.results[i];
                        j++;
                    }
                }
            }

            function changeErrorFn(data){
                console.error(data.data);
            }
        }

        function change(url){
            Team.change(url).then(changeSuccessFn, changeErrorFn);

            function changeSuccessFn(data){
                vm.team = data.data;
                var j = 0;
                vm.teamsFound = [];
                console.log(vm.team);
                for(var i = 0; i<vm.team.results.length; i++){
                    if(vm.team.results[i].name === search){
                        vm.teamsFound[j] = vm.team.results[i];
                        j++;
                    }
                }
            }

            function changeErrorFn(data){
                console.error(data.data);
            }
        }
    }
})();