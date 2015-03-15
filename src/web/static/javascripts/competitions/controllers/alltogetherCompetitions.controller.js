(function(){

    'use strict';

    angular
        .module('ciberonline.competitions.controllers')
        .controller('AllTogetherCompetitionsController', AllTogetherCompetitionsController);

    AllTogetherCompetitionsController.$inject = ['$location', 'Competition'];

    function AllTogetherCompetitionsController($location, Competition){
        var vm = this;
        activate();

        function activate(){
            Competition.getAll().then(getAllSuccessFn, getAllErrorFn);

            function getAllSuccessFn(data, status, headers, config){
                vm.competitions = data.data;
            }

            function getAllErrorFn(data, status, headers, config){
                console.error(data.data);
                $location.url('/panel/');
            }

        }

    }

})();

