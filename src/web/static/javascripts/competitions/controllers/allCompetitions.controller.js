(function(){

    'use strict';

    angular
        .module('ciberonline.competitions.controllers')
        .controller('AllCompetitionsController', AllCompetitionsController);

    AllCompetitionsController.$inject = ['$location', 'Competition'];

    function AllCompetitionsController($location, Competition){
        var vm = this;
        activate();

        function activate(){
            Competition.getAll().then(getAllSuccessFn, getAllErrorFn);

            function getAllSuccessFn(data, status, headers, config){
                vm.competitions = data.data;
                console.log(vm.competitions[0].type_of_competition);
            }

            function getAllErrorFn(data, status, headers, config){
                console.error(data.data);
                $location.url('/panel/');
            }

        }


    }

})();
