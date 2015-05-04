(function(){

    'use strict';

    angular
        .module('ciberonline.soloTrials.controllers')
        .controller('SoloByUserController', SoloByUserController);

    SoloByUserController.$inject = ['SoloTrials', '$routeParams', 'Round'];

    function SoloByUserController(SoloTrials, $routeParams, Round){
        var vm = this;
        activate();

        function activate(){
            SoloTrials.getAll().then(getAllSuccessFn, getAllErrorFn);

            function getAllSuccessFn(data){
                vm.solos = data.data;
                console.log(vm.solos);
                Round.getResources().then(success, error);

                function success(data){
                    vm.resources = data.data;
                    console.log(vm.resources);
                }

                function error(data){
                    console.error(data.data);
                }
            }


            function getAllErrorFn(data){
                console.error(data.data);
            }


        }

    }

})();