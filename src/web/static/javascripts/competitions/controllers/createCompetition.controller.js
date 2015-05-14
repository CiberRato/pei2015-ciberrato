(function () {
    'use strict';

    angular
        .module('ciberonline.competitions.controllers')
        .controller('CreateCompetitionController', CreateCompetitionController);

    CreateCompetitionController.$inject = ['$location', 'Competition', 'Round', '$scope'];

    function CreateCompetitionController($location, Competition, Round, $scope){
        var vm = this;

        vm.create = create;
        vm.typesToShow = [];

        activate();

        function activate(){
            $scope.loader = {
                loading: false
            };

            Competition.getAllTypesOfCompetition().then(getAllSuccessFn, getAllErrorFn);

            function getAllSuccessFn(data){
                vm.typesOfCompetition = data.data;
                vm.tmp = data.data;
                console.log(vm.tmp.results);
                vm.typesToShow = vm.tmp.results;
                console.log(vm.typesToShow);
                console.log(vm.tmp);

                if(vm.tmp.next != null){
                    add(vm.tmp.next);
                }
                console.log(vm.tmp);
                console.log(vm.typesToShow);

                $scope.loader = {
                    loading: true
                };

            }

            function add(url){
                Competition.change(url).then(addSuccessFn, addErrorFn);

                function addSuccessFn(data){
                    vm.tmp = data.data;
                    for(var i=0; i<vm.tmp.results.length; i++){
                        vm.typesToShow.push(vm.tmp.results[i]);
                    }
                    if(vm.tmp.next != null){
                        add(vm.tmp.next);
                    }


                }

                function addErrorFn(data){
                    console.error(data.data);
                }
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
                        theme: 'jGrowl-notification ui-state-highlight ui-corner-all success'
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
                        theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
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
                    theme: 'jGrowl-notification ui-state-highlight ui-corner-all danger'
                });
            }

        }

    }
})();

