(function () {
    'use strict';

    angular
        .module("ciberonline.notifications.services")
        .factory("Notification", Notification);

    function Notification(){
        var events = (function(){
          var topics = {};
          var hOP = topics.hasOwnProperty;

          var hasSubscribed = function(topicSubscribed){
            for (var topic in topics){
              if(topics.hasOwnProperty(topic)){
                if(topic==topicSubscribed){
                  return true;
                }
              }
            }
            return false;
          };

          return {
            subscribe: function(topic, listener) {
              if(hasSubscribed(topic)){
                return {
                  remove: function() {
                    delete topics[topic][0];
                  }
                };
              }else{
                // Create the topic's object if not yet created
                if(!hOP.call(topics, topic)) topics[topic] = [];

                // Add the listener to queue
                var index = topics[topic].push(listener) -1;

                // Provide handle back for removal of topic
                return {
                  remove: function() {
                    delete topics[topic][index];
                  }
                };
              }
            },
            publish: function(topic, info) {
              // If the topic doesn't exist, or there's no listeners in queue, just leave
              if(!hOP.call(topics, topic)) return;

              // Cycle through topics queue, fire!
              topics[topic].forEach(function(item) {
                    item(info != undefined ? info : {});
              });
            }
          };
        })();

        var Notification = {
            events: events
        };

        return Notification;
    }
})();