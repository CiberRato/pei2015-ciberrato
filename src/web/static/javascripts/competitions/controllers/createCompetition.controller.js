(function () {
    'use strict';

    angular
        .module('ciberonline.competitions.controllers')
        .controller('CreateCompetitionController', CreateCompetitionController);

    CreateCompetitionController.$inject = ['$location', 'Authentication', 'Competition', 'Round'];

    function CreateCompetitionController($location, Authentication, Competition, Round){
        var vm = this;

        vm.create = create;

        var username;

        activate();

        function activate(){
            var authenticatedAccount = Authentication.getAuthenticatedAccount();
            username = authenticatedAccount.username;

            Competition.getAllTypesOfCompetition().then(getAllSuccessFn, getAllErrorFn);

            function getAllSuccessFn(data){
                vm.typesOfCompetition = data.data;
                console.log(vm.typesOfCompetition);
            }

            function getAllErrorFn(data){
                console.error(data.data);
                $location.path('/admin/');
            }

        }

        function create(){
            var x;
            if(vm.typesOfCompetition.count > 0) {
                x = document.getElementById("select").value;
            }else {
                x = undefined;
            }

            Competition.create(vm.competitionName, x).then(createSuccessFn, createErrorFn);


            function createSuccessFn(){
                Round.createRound(vm.firstRound, vm.competitionName).then(createRoundSuccessFn, createRoundErrorFn);

                function createRoundSuccessFn(){
                    $.jGrowl("Competition has been created successfully.", {
                        life: 2500,
                        theme: 'success'
                    });
                    $location.path('/admin/allCompetitions/');
                }

                function createRoundErrorFn(data){
                    var errors = "";
                    for (var value in data.data.message) {
                        errors += "&bull; Round " + value.replace("_", " ") + ":<br/>"
                        for (var error in data.data.message[value]){
                            errors += " &nbsp; "+ data.data.message[value][error] + '<br/>';
                        }
                    }
                    $.jGrowl(errors, {
                        life: 5000,
                        theme: 'btn-danger'
                    });
                }

            }

            function createErrorFn(data){
                var errors = "";
                for (var value in data.data.message) {
                    errors += "&bull; Competition " + value.replace("_", " ") + ":<br/>"
                    for (var error in data.data.message[value]){
                        errors += " &nbsp; "+ data.data.message[value][error] + '<br/>';
                    }
                }
                $.jGrowl(errors, {
                    life: 5000,
                    theme: 'btn-danger'
                });
            }

        }

    }
})();

