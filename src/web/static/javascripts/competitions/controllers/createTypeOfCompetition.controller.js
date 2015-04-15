(function () {
    'use strict';

    angular
        .module('ciberonline.competitions.controllers')
        .controller('CreateTypeOfCompetitionController', CreateTypeOfCompetitionController);

    CreateTypeOfCompetitionController.$inject = ['$location', 'Authentication', 'Competition', 'Round'];

    function CreateTypeOfCompetitionController($location, Authentication, Competition){
        var vm = this;

        vm.create = create;

        var username;

        activate();

        function activate(){
            var authenticatedAccount = Authentication.getAuthenticatedAccount();
            username = authenticatedAccount.username;

        }

        function create(){
            Competition.createTypeOfCompetition(vm.typeOfCompetitionName, vm.teamsForTrial, vm.agentsByGrid).then(createSuccessFn, createErrorFn);

            function createSuccessFn(){
                $.jGrowl("Type Of Competition has been created successfully.", {
                    life: 2500,
                    theme: 'success'
                });
                $location.path('/admin/allTypesOfCompetition/');

            }

            function createErrorFn(data){
                console.error(data.data);
                $.jGrowl("Type Of Competition could not be created.", {
                    life: 2500,
                    theme: 'btn-danger'
                });
            }

        }

    }
})();

