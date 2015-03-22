(function(){
    'use strict';

    angular
        .module('ciberonline.search.controllers')
        .controller('SearchController', SearchController);

    SearchController.$inject = ['$location', '$routeParams','Team', 'Profile', 'Competition'];

    function SearchController($location, $routeParams, Team, Profile, Competition){
        var vm = this;
        var search = $routeParams.search;

        activate();

        function activate(){
            Team.getByName(search).then(getAllSuccessFn, getAllErrorFn);
            Profile.get(search).then(getByUsernameSuccessFn, getByUsernameErrorFn);
            Profile.getByFirstName(search).then(getByFirstNameSuccessFn, getByFirstNameErrorFn);
            Profile.getByLastName(search).then(getByLastNameSuccessFn, getByLastNameErrorFn);
            Competition.getByName(search).then(getAllCompetitionsSuccessFn, getAllCompetitionsErrorFn);

            function getAllSuccessFn(data){
                vm.team = data.data;
            }

            function getAllErrorFn(data){
                console.error(data.data);
                $location.path('/panel/');
            }

            function getByUsernameSuccessFn(data){
                vm.members = data.data;
            }

            function getByUsernameErrorFn(data){
                console.error(data.data);
                $location.path('/panel/');
            }

            function getByFirstNameSuccessFn(data){
                vm.members.append(data.data);
            }

            function getByFirstNameErrorFn(data){
                console.error(data.data);
                $location.path('/panel/');
            }

            function getByLastNameSuccessFn(data){
                vm.members.append(data.data);
            }

            function getByLastNameErrorFn(data){
                console.error(data.data);
                $location.path('/panel/');
            }

            function getAllCompetitionsSuccessFn(data){
                vm.competitions = data.data;
            }

            function getAllCompetitionsErrorFn(data){
                console.error(data.data);
                $location.path('/panel/');
            }
        }
    }
})();