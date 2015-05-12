(function(){

    'use strict';

    angular
        .module('ciberonline.competitions.controllers')
        .controller('MyCompetitionsController', MyCompetitionsController);

    MyCompetitionsController.$inject = ['$location', '$routeParams', 'Competition', 'Authentication', 'cfpLoadingBar'];

    function MyCompetitionsController($location, $routeParams, Competition, Authentication, cfpLoadingBar){
        var vm = this;
        vm.getScoresByCompetition = getScoresByCompetition;
        activate();

        function activate(){
            cfpLoadingBar.start();

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


            function getAllSuccessFn(data) {
                vm.competitions = data.data;
                console.log(vm.competitions);
                Competition.getMyCompetitions().then(getMyCompetitionsSuccessFn, getMyCompetitionsErrorFn);

                function getMyCompetitionsSuccessFn(data){
                    vm.myCompetitions = data.data;
                    console.log(data.data);
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
            }

            function getAllErrorFn(data) {
                console.error(data.data);
                $location.path('/panel/')
            }

            cfpLoadingBar.complete();


        }


        function getScoresByCompetition(){
            Competition.getScoresByCompetition(vm.competitionName).then(getScoresByCompetitionSuccessFn, getScoresByCompetitionErrorFn);

            function getScoresByCompetitionSuccessFn(data){
                vm.scoresByCompetition = data.data;
            }

            function getScoresByCompetitionErrorFn(data){
                console.error(data.data);
            }
        }

    }

})();