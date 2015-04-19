(function(){

    'use strict';

    angular
        .module('ciberonline.competitions.controllers')
        .controller('AllTypesOfCompetitionController', AllTypesOfCompetitionController);

    AllTypesOfCompetitionController.$inject = ['$location', 'Competition', '$route'];

    function AllTypesOfCompetitionController($location, Competition, $route){
        var vm = this;
        vm.deleteTypeOfCompetition = deleteTypeOfCompetition;
        vm.change = change;
        activate();


        function activate(){
            Competition.getAllTypesOfCompetition().then(getAllSuccessFn, getAllErrorFn);

            function getAllSuccessFn(data){
                vm.typesOfCompetitions = data.data;
            }

            function getAllErrorFn(data){
                console.error(data.data);
                $location.url('/panel/');
            }

        }

        function deleteTypeOfCompetition(name){
            Competition.removeTypeOfCompetition(name).then(removeSuccessFn, removeErrorFn);

            function removeSuccessFn(){
                $.jGrowl("Type Of Competition has been removed successfully.", {
                    life: 2500,
                    theme: 'success'
                });

                $route.reload();
            }

            function removeErrorFn(data){
                console.error(data.data);
                $.jGrowl(data.data.message, {
                    life: 2500,
                    theme: 'btn-danger'
                });
            }
        }

        function change(url){
            Competition.change(url).then(changeSuccessFn, changeErrorFn);

            function changeSuccessFn(data){
                vm.typesOfCompetitions = data.data;
            }

            function changeErrorFn(data){
                console.error(data.data);
            }
        }



    }

})();