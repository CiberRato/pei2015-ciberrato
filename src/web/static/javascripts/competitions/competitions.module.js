(function (){
    'use strict';

    angular
        .module('ciberonline.competitions', [
            'ciberonline.competitions.controllers',
            'ciberonline.competitions.services'
        ]);

    angular
        .module('ciberonline.competitions.controllers', []);

    angular
        .module('ciberonline.competitions.services', ['ngCookies']);
})();