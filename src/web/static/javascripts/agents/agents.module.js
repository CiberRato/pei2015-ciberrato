(function (){
    'use strict';

    angular
        .module('ciberonline.agents', [
            'ciberonline.agents.controllers',
            'ciberonline.agents.services'
        ]);

    angular
        .module('ciberonline.agents.controllers', []);

    angular
        .module('ciberonline.agents.services', ['ngCookies']);
})();