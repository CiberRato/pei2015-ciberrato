(function(){

    'use strict';

    angular
        .module('ciberonline.agents.controllers')
        .controller('AgentDetailController', AgentDetailController);

    AgentDetailController.$inject = ['$location', '$routeParams', 'Competition', 'Team', 'Agent'];

    function AgentDetailController($location, $routeParams, Competition, Team, Agent) {
        var vm = this;
        var agentName = $routeParams.name;

        activate();

        function activate() {
            Agent.getAgent(agentName).then(getAgentSuccessFn, getAgentErrorFn);

            function getAgentSuccessFn(data, status, headers, config) {
                vm.agent = data.data;

                $('.plupload').pluploadQueue({
                    runtimes : 'html5,gears,flash,silverlight,browserplus',
                    url : '/api/v1/competitions/upload/agent/?agent_name='+vm.agent.agent_name+'&language='+$("#selector_language").find(":selected").text(),
                    max_file_size : '10mb',
                    chunk_size : '1mb',
                    unique_names : true,
                    resize : {width : 320, height : 240, quality : 90},
                    flash_swf_url : 'js/plugins/plUpload/plupload.flash.swf',
                    silverlight_xap_url : 'js/plugins/plUpload/plupload.silverlight.xap'
                });

                $(".plupload_header").remove();
                $(".plupload_progress_container").addClass("progress").addClass('progress-striped');
                $(".plupload_progress_bar").addClass("bar");
                $(".plupload_button").each(function(e){
                    if($(this).hasClass("plupload_add")){
                        $(this).attr("class", 'btn btn-primary btn-alt pl_add btn-small');
                    } else {
                        $(this).attr("class", 'btn btn-success btn-alt pl_start btn-small');
                    }
                });
            }

            function getAgentErrorFn(data, status, headers, config) {
                console.error(data.data);
                $location.url('/panel/');
            }
        }
    }

})();
