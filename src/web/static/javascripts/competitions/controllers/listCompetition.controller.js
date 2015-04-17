(function(){

    'use strict';

    angular
        .module('ciberonline.competitions.controllers')
        .controller('ListCompetitionController', ListCompetitionController);

    ListCompetitionController.$inject = ['$location', '$route', '$routeParams', 'Competition', 'Round'];

    function ListCompetitionController($location, $route, $routeParams, Competition, Round){
        var vm = this;
        vm.competitionName = $routeParams.name;
        vm.startSimulation = startSimulation;
        vm.validateInscription = validateInscription;

        activate();

        function activate() {
            Competition.getCompetition(vm.competitionName).then(getCompetitionSuccessFn, getCompetitionErrorFn);
            Competition.getAllRounds(vm.competitionName).then(getAllRoundsSuccessFn, getAllRoundsErrorFn);

            function getCompetitionSuccessFn(data){
                vm.competition = data.data;
                Competition.getTeams(vm.competitionName).then(getTeamsSuccessFn, getTeamsErrorFn);

                function getTeamsSuccessFn(data) {
                    vm.competitionTeamsInfo = data.data;
                }

                function getTeamsErrorFn(data) {
                    console.error(data.data);
                    $location.url('/panel/');
                }
            }

            function getCompetitionErrorFn(data){
                console.error(data.data);
                $location.path('/panel/');
            }

            function getAllRoundsSuccessFn(data){
                vm.rounds = data.data;
                for(var i = 0; i<vm.rounds.length; i++){
                    getSimulations(vm.rounds[i].name, i);
                }
            }

            function getSimulations(roundName, i){
                Round.getSimulations(roundName).then(getSimulationsSuccessFn, getSimulationsErrorFn);

                function getSimulationsSuccessFn(data){
                    vm.rounds[i].simulations = data.data;
                }

                function getSimulationsErrorFn(data){
                    console.error(data.data);
                    $location.path('/panel/');

                }
            }

            function getAllRoundsErrorFn(data){
                console.error(data.data);
                $location.path('/panel/');
            }
        }

        function startSimulation(identifier){
            console.log(identifier);
            Round.startSimulation(identifier).then(startSimulationSuccessFn, startSimulationErrorFn);

            function startSimulationSuccessFn(){
                $.jGrowl("Simulation has been started successfully.", {
                    life: 2500,
                    theme: 'success'
                });
                $route.reload();
            }

            function startSimulationErrorFn(){
                $.jGrowl(data.data.message, {
                    life: 2500,
                    theme: 'btn-danger'
                });
                $route.reload();
            }

        }
        function validateInscription(group_name, competition_name){
            Competition.validateInscription(group_name, competition_name).then(validateInscriptionSuccessFn, validateInscriptionErrorFn);

            function validateInscriptionSuccessFn(){
                $route.reload();            }
            function validateInscriptionErrorFn(data){
                console.error(data.data);
                $location.path('/admin/');
            }

        }


    }

})();
