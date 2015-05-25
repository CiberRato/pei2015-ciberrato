(function (){
    'use strict';

    angular
        .module('ciberonline.authentication.controllers')
        .controller('PanelController', PanelController);

    PanelController.$inject = ['$location', '$dragon', '$scope'];

    function PanelController($location, $dragon, $scope){
        var vm = this;

        activate();

        function activate(){
        }


    }
})();