(function () {
    'use strict';

    angular
        .module("ciberonline.notifications.services")
        .factory("Notification", Notification);

    function Notification(){
          var events = (function(){
          var slotTopics0 = {};
          var slotTopics1 = {};
          var hOP0 = slotTopics0.hasOwnProperty;
          var hOP1 = slotTopics1.hasOwnProperty;

          var hasSubscribed = function(topicSubscribed, slot){
            if(slot==0){
              for (var topic0 in slotTopics0){
                if(slotTopics0.hasOwnProperty(topic0)){
                  if(topic0==topicSubscribed){
                    return true;
                  }
                }
              }
              return false;
            }else if (slot==1) {
              for (var topic1 in slotTopics1){
                if(slotTopics1.hasOwnProperty(topic1)){
                    console.log("topic1" + topic1);
                  if(topic1==topicSubscribed){
                    return true;
                  }
                }
              }
              return false;
            }else{
              return true;
            }
          };

          return {
            subscribe: function(topic, slot, listener) {
                console.log("topic" + topic + "slot" +slot);
                console.log(listener);
              if(hasSubscribed(topic, slot)){
                if(slot==0){
                    console.log("FUI PARA AQUI1");
                  return {
                    remove: function() {
                      delete slotTopics0[topic][0];
                    }
                  };
                }else if (slot==1) {
                    console.log("FUI PARA AQUI2");
                    console.log(slotTopics1[topic][0]);
                    console.log(slotTopics1);
                  return {
                    remove: function() {
                      delete slotTopics1[topic][0];
                    }
                  };
                }
              }else{
                if(slot==0){
                  // Create the topic's object if not yet created
                  if(!hOP0.call(slotTopics0, topic)) slotTopics0[topic] = [];

                  // Add the listener to queue
                  var index = slotTopics0[topic].push(listener) -1;

                  // Provide handle back for removal of topic
                  return {
                    remove: function() {
                      slotTopics0 = {};
                    }
                  };
                }else if (slot==1) {
                  // Create the topic's object if not yet created
                  if(!hOP1.call(slotTopics1, topic)) slotTopics1[topic] = [];

                  // Add the listener to queue
                  var index = slotTopics1[topic].push(listener) -1;

                  // Provide handle back for removal of topic
                  return {
                    remove: function() {
                      slotTopics1 = {};
                        console.log("aquipa");
                        console.log(slotTopics1);
                    }
                  };
                }
              }
            },
            publish: function(topic, info) {
              // slotTopics0
              // If the topic doesn't exist, or there's no listeners in queue, just leave
              if(!hOP0.call(slotTopics0, topic)) return;

              // Cycle through topics queue, fire!
              slotTopics0[topic].forEach(function(item) {
                    item(info != undefined ? info : {});
              });

              // slotTopics1
              // If the topic doesn't exist, or there's no listeners in queue, just leave
              if(!hOP1.call(slotTopics1, topic)) return;

              // Cycle through topics queue, fire!
              slotTopics1[topic].forEach(function(item) {
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