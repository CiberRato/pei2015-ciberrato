(function(){

    'use strict';

    angular
        .module('ciberonline.competitions.controllers')
        .controller('MyCompetitionsController', MyCompetitionsController);

    MyCompetitionsController.$inject = ['$location', '$routeParams', 'Competition', 'Authentication'];

    function MyCompetitionsController($location, $routeParams, Competition, Authentication){
        var vm = this;
        activate();

        function activate(){
            var authenticatedAccount = Authentication.getAuthenticatedAccount();
            var username = $routeParams.username;

            if(!authenticatedAccount){
                $location.url('/');
            }else{
                if(authenticatedAccount.username !== username){
                    $location.url('/');
                }
            }

            Competition.getAll().then(getAllSuccessFn, getAllErrorFn);
            Competition.getMyCompetitions(username).then(getMyCompetitionsSuccessFn, getMyCompetitionsErrorFn);

            function getMyCompetitionsSuccessFn(data){
                vm.myCompetitions = data.data;
                for(var i = 0; i<vm.myCompetitions.length; i++){
                    for(var j = 0; j<vm.competitions.length; j++){
                        if(vm.myCompetitions[i].competition_name === vm.competitions[j].name){
                            vm.myCompetitions[i].state = vm.competitions[j].state_of_competition;
                            vm.myCompetitions[i].type = vm.competitions[j].type_of_competition;
                        }
                    }
                }
                console.log(vm.myCompetitions);
            }

            function getMyCompetitionsErrorFn(data){
                console.error(data.data);
                $location.url('/panel/');
            }

            function getAllSuccessFn(data) {
                vm.competitions = data.data;
            }

            function getAllErrorFn(data) {
                console.error(data.data);
                $location.path('/panel/')
            }

        }

    }

})();