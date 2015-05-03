(function(){

    'use strict';

    angular
        .module('ciberonline.soloTrials.controllers')
        .controller('SoloByTeamController', SoloByTeamController);

    SoloByTeamController.$inject = ['SoloTrials', '$routeParams', 'Round'];

    function SoloByTeamController(SoloTrials, $routeParams, Round){
        var vm = this;
        vm.competitionName = $routeParams.identifier;
        vm.teamName = $routeParams.teamName;
        activate();

        function activate(){
            SoloTrials.getByTeam(vm.competitionName).then(getByTeamSuccessFn, getByTeamErrorFn);

            function getByTeamSuccessFn(data){
                vm.solos = data.data;
                console.log(vm.solos);
            }


            function getByTeamErrorFn(data){
                console.error(data.data);
            }


        }

    }

})();