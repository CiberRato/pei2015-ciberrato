(function(){

    'use strict';

    angular
        .module('ciberonline.soloTrials.controllers')
        .controller('SoloByUserController', SoloByUserController);

    SoloByUserController.$inject = ['SoloTrials', '$scope', 'Round'];

    function SoloByUserController(SoloTrials, $scope, Round){
        var vm = this;
        activate();

        function activate(){
            $scope.loader = {
                loading: false
            };
            SoloTrials.getAll().then(getAllSuccessFn, getAllErrorFn);

            function getAllSuccessFn(data){
                vm.solos = data.data;
                console.log(vm.solos);
                Round.getResources().then(success, error);

                function success(data){
                    vm.resources = data.data;
                    console.log(vm.resources);
                    $scope.loader = {
                        loading: true
                    };
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