(function (){
    'use strict';

    angular
        .module('ciberonline.hallOfFame', [
            'ciberonline.hallOfFame.controllers',
            'ciberonline.hallOfFame.services'
        ]);

    angular
        .module('ciberonline.hallOfFame.controllers', []);

    angular
        .module('ciberonline.hallOfFame.services', ['ngCookies']);
})();