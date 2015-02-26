var x2js = new X2JS();
function labConvertXml2JSon() {
    return JSON.stringify(x2js.xml_str2json($("#labXML").val()));
}
function gridConvertXml2JSon() {
    return JSON.stringify(x2js.xml_str2json($("#gridXML").val()));
}
function robotConvertXml2JSon() {
    return JSON.stringify(x2js.xml_str2json($("#robotXML").val()));
}

function convertToStringPoints(cornerList, zoom){
    var out = "";
    var b = 0;
    for(; b<cornerList.Corner.length; b++){
        out+= cornerList.Corner[b]._X*zoom + "," + cornerList.Corner[b]._Y*zoom + " ";
    }
    return out;
}


function turn90(PosList){
    for(i=0; i<PosList.Robot.length; i++){
        PosList.Robot[i].Position._Dir = parseInt(PosList.Robot[i].Position._Dir)+90;
    }
    return PosList;
}


angular.module('myapp', [])
    .controller('ctrl', ['$scope', '$timeout', function($scope, $timeout){
        $scope.zoom = 30;

        var robot_json_object = robotConvertXml2JSon();
        var robot_obj = angular.fromJson(robot_json_object);
        var grid_json_object = gridConvertXml2JSon();
        var grid_obj = angular.fromJson(grid_json_object);
        var lab_json_object = labConvertXml2JSon();
        var lab_obj = angular.fromJson(lab_json_object);

        for(i=0; i<lab_obj.Lab.Wall.length; i++){
            lab_obj.Lab.Wall[i].str = convertToStringPoints(lab_obj.Lab.Wall[i], $scope.zoom);
        }
        console.log(robot_obj);

        $scope.beacon_height = lab_obj.Lab.Beacon._Height;
        $scope.map = lab_obj.Lab;
        $scope.grid = grid_obj.Grid;
        $scope.timeline = turn90(robot_obj.PosList);
        $scope.robot = $scope.timeline.Robot[0].Position;
        $scope.stats = $scope.timeline.Robot[0];

        $scope.idx = 1;
        var refresh_rate = 50;
        var pause = 0;

        var tick = function() {
            try{
                $scope.robot = $scope.timeline.Robot[$scope.idx].Position;
                $scope.stats = $scope.timeline.Robot[$scope.idx];
                console.log($scope.timeline.Robot[$scope.idx]);
                $(".leftGrip").css("left", ($scope.idx*820)/1800);
                $scope.idx++;
            }catch(TypeError){
                $scope.pause();
            }
            if(!pause){
                $timeout(tick, refresh_rate);
            }
        };

        $scope.play = function() {
            pause = 0;
            $timeout(tick, refresh_rate);
        };

        $scope.pause = function(){
            pause = 1;
        };
    }])

    .directive('ngCx', function() {
        return function(scope, element, attrs) {
            scope.$watch(attrs.ngCx, function(value) {
                element.attr('cx', value);
            });
        };
    })
    .directive('ngCy', function() {
        return function(scope, element, attrs) {
            scope.$watch(attrs.ngCy, function(value) {
                element.attr('cy', value);
            });
        };
    })
    .directive('ngX', function() {
        return function(scope, element, attrs) {
            scope.$watch(attrs.ngX, function(value) {
                element.attr('x', value);
            });
        };
    })
    .directive('ngY', function() {
        return function(scope, element, attrs) {
            scope.$watch(attrs.ngY, function(value) {
                element.attr('y', value);
            });
        };
    })
    .directive('ngR', function() {
        return function(scope, element, attrs) {
            scope.$watch(attrs.ngR, function(value) {
                element.attr('r', value);
            });
        };
    })
    .directive('ngH', function() {
        return function(scope, element, attrs) {
            scope.$watch(attrs.ngH, function(value) {
                element.attr('height', value);
            });
        };
    })
    .directive('ngW', function() {
        return function(scope, element, attrs) {
            scope.$watch(attrs.ngW, function(value) {
                element.attr('width', value);
            });
        };
    })
    .directive('ngT', function() {
        return function(scope, element, attrs) {
            scope.$watch(attrs.ngT, function() {
                console.log(attrs.ngT);
                element.attr('transform', attrs.ngT);
            });
        };
    })
    .directive('ngPoints', function() {
        return function(scope, element, attrs) {
            scope.$watch(attrs.ngPoints, function(value) {
                element.attr('points', value);
            });
        };
    })
    .directive('conversation', function() {
        return {
            restrict: 'E',
            replace: true,
            compile: function(tElement, attr) {
                attr.$observe('typeId', function(data) {
                    console.log("Updated data ", data);
                }, true);

            }
        };
    });


angular.element(document).ready(function(){
    angular.bootstrap(document, ['myapp']);
});
