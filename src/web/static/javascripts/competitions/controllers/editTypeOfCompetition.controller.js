(function () {
    'use strict';

    angular
        .module('ciberonline.teams.controllers')
        .controller('EditTypeOfCompetitionController', EditTypeOfCompetitionController);

    EditTypeOfCompetitionController.$inject = ['$location', '$routeParams', 'Competition'];

    function EditTypeOfCompetitionController($location, $routeParams, Competition){
        var vm=this;
        var typeName;
        vm.update = update;

        activate();

        function activate(){
            typeName = $routeParams.name;

            Competition.getType(typeName).then(getTypeSuccessFn, getTypeErrorFn);

            function getTypeSuccessFn(data){
                vm.type = data.data;
                console.log(vm.type);
            }

            function getTypeErrorFn(data){
                console.error(data.data);
                $location.url('/panel/');
            }
        }

        function update(){
            Competition.updateType(vm.type, typeName).then(updateTeamSuccessFn, updateTeamErrorFn);

            function updateTeamSuccessFn(){
                $.jGrowl("Team has been updated.", {
                    life: 2500,
                    theme: 'success'
                });
                $location.path("/admin/allTypesOfCompetition");
            }

            function updateTeamErrorFn(data){
                $.jGrowl("Team could not be updated.", {
                    life: 2500,
                    theme: 'btn-danger'
                });
                console.error(data.data);
            }
        }

    }
})();