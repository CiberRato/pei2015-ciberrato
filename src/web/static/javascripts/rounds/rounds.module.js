(function (){
    'use strict';

    angular
        .module('ciberonline.rounds', [
            'ciberonline.rounds.controllers',
            'ciberonline.rounds.services'
        ]);

    angular
        .module('ciberonline.rounds.controllers', []);

    angular
        .module('ciberonline.rounds.services', ['ngCookies']);
})();