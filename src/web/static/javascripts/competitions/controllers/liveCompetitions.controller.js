(function(){

    'use strict';

    angular
        .module('ciberonline.competitions.controllers')
        .controller('LiveCompetitionsController', LiveCompetitionsController);

    LiveCompetitionsController.$inject = ['$location', 'Competition'];

    function LiveCompetitionsController($location, Competition){
        var vm = this;
        activate();

        function activate(){
            Competition.getLive().then(getLiveSuccessFn, getLiveErrorFn);

            function getLiveSuccessFn(data){
                vm.competitions = data.data;
                for(var i = 0; i<vm.competitions.length; i++){
                    getTeams(vm.competitions[i].name, i);
                }
            }

            function getLiveErrorFn(data){
                console.error(data.data);
                $location.url('/panel/');
            }

            function getTeams(competitionName, i) {
                Competition.getTeams(competitionName).then(getTeamsSuccessFn, getTeamsErrorFn);


                function getTeamsSuccessFn(data, status, headers, config) {
                    vm.teams = data.data;
                    vm.competitions[i].allTeams = vm.teams.length;
                }

                function getTeamsErrorFn(data, status, headers, config) {
                    console.error(data.data);
                    $location.path('/panel/')
                }
            }

        }

    }

})();


