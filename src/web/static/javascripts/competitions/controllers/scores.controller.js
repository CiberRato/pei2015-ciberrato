(function () {
    'use strict';

    angular
        .module('ciberonline.competitions.controllers')
        .controller('ScoresController', ScoresController);

    ScoresController.$inject = ['$location', '$routeParams', 'Competition', 'Round'];

    function ScoresController($location, $routeParams, Competition, Round){
        var vm = this;

        activate();

        function activate(){
            vm.competitionName = $routeParams.name;
            Competition.getCompetition(vm.competitionName).then(getCompetitionSuccessFn, getCompetitionErrorFn);

            function getCompetitionSuccessFn(data){
                vm.competition = data.data;
                console.log(vm.competition);
            }

            function getCompetitionErrorFn(data){
                console.error(data.data);
                $location.path('/panel/');
            }

        }

    }
})();
