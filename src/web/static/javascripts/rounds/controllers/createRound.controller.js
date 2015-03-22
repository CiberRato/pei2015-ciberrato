(function(){

    'use strict';

    angular
        .module('ciberonline.rounds.controllers')
        .controller('CreateRoundController', CreateRoundController);

    CreateRoundController.$inject = ['$location', '$route', '$routeParams', 'Round'];

    function CreateRoundController($location, $route, $routeParams, Round){
        var vm = this;

        vm.create = create;
        vm.competitionName = $routeParams.name;
        activate();

        function activate() {

        }

        function create(){
            Round.create(vm.roundName, vm.competitionName).then(createSuccessFn, createErrorFn);

            function createSuccessFn(){
                $.jGrowl("Round has been created successfully.", {
                    life: 2500,
                    theme: 'success'
                });
                $location.path('/admin/' + vm.competitionName + "/");
            }

            function createErrorFn(data){
                console.error(data.data);
                $.jGrowl("Round can't be created.", {
                    life: 2500,
                    theme: 'btn-danger'
                });
                $route.reload();
            }
        }

    }

})();


