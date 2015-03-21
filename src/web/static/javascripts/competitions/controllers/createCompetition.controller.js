(function () {
    'use strict';

    angular
        .module('ciberonline.competitions.controllers')
        .controller('CreateCompetitionController', CreateCompetitionController);

    CreateCompetitionController.$inject = ['$location', 'Authentication', 'Competition'];

    function CreateCompetitionController($location, Authentication, Competition){
        var vm = this;

        vm.create = create;

        var username;

        activate();

        function activate(){
            var authenticatedAccount = Authentication.getAuthenticatedAccount();
            username = authenticatedAccount.username;

        }

        function create(){
            var x = document.getElementById("select").value;
            console.log(x + ' ' + vm.competitionName + ' ' + vm.firstRound);
            Competition.create(vm.competitionName, x).then(createSuccessFn, createErrorFn);

            function createSuccessFn(){
                Competition.createRound(vm.firstRound, vm.competitionName).then(createRoundSuccessFn, createRoundErrorFn);

                function createRoundSuccessFn(){
                    $.jGrowl("Competition has been created successfully.", {
                        life: 2500,
                        theme: 'success'
                    });
                    $location.path('/admin/allCompetitions/');
                }

                function createRoundErrorFn(data){
                    console.error(data.data);
                    $.jGrowl("Round could not be created.", {
                        life: 2500,
                        theme: 'btn-danger'
                    });
                }

            }

            function createErrorFn(data){
                console.error(data.data);
                $.jGrowl("Competition could not be created.", {
                    life: 2500,
                    theme: 'btn-danger'
                });
            }

        }

    }
})();

