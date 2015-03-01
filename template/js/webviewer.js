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
        var b = 0;
        var play = 0;

        for(i=0; i<lab_obj.Lab.Wall.length; i++){
            lab_obj.Lab.Wall[i].str = convertToStringPoints(lab_obj.Lab.Wall[i], $scope.zoom);
        }

        $scope.beacon_height = lab_obj.Lab.Beacon._Height;
        $scope.map = lab_obj.Lab;
        $scope.grid = grid_obj.Grid;
        $scope.timeline = turn90(robot_obj.PosList);
        $scope.robot = $scope.timeline.Robot[0].Position;
        $scope.stats = $scope.timeline.Robot[0];
        $scope.idx = 1;
        $scope.refresh_rate = 50;
        $scope.pline = "";
        $scope.last_idx = 0;
        $scope.robotColor = 'img/svg/mickey_red_smile.svg';
        $scope.groundColor = 'black';
        $scope.cheeseColor = 'img/svg/cheese.svg';
        $scope.circleBorder = '#00ffff';
        $scope.greatWallColor = '#008000';
        $scope.smallWallColor = '#0000ff';
        $scope.gridColor = '#cfd4db';

        var refresh = function(refresh_rate){
            $timeout(tick, refresh_rate);
        }

        var tick = function() {
            try{
                $scope.robot = $scope.timeline.Robot[$scope.idx].Position;
                $scope.stats = $scope.timeline.Robot[$scope.idx];

                if(($scope.last_idx+1)!=$scope.idx){

                    $scope.pline ="";
                    for(b=0;b<$scope.idx;b++){
                        $scope.pline += $scope.timeline.Robot[b].Position._X*$scope.zoom + "," + $scope.timeline.Robot[b].Position._Y*$scope.zoom + " ";
                    }
                }else{
                    $scope.pline += $scope.timeline.Robot[$scope.idx].Position._X*$scope.zoom + "," + $scope.timeline.Robot[$scope.idx].Position._Y*$scope.zoom + " ";
                }
                $scope.last_idx = $scope.idx;

                $(".leftGrip").css("left", ($scope.idx*820)/1800);
                if(play){
                    $scope.idx++;
                }
            }catch(TypeError){
                $scope.stop();
            }
            if(play){
                refresh($scope.refresh_rate);
            }
        };

        $scope.refreshSVG = function(){
            $scope.robot = $scope.timeline.Robot[$scope.idx].Position;
            $scope.stats = $scope.timeline.Robot[$scope.idx];

            if(($scope.last_idx+1)!=$scope.idx){

                $scope.pline ="";
                for(b=0;b<$scope.idx;b++){
                    $scope.pline += $scope.timeline.Robot[b].Position._X*$scope.zoom + "," + $scope.timeline.Robot[b].Position._Y*$scope.zoom + " ";
                }
            }else{
                $scope.pline += $scope.timeline.Robot[$scope.idx].Position._X*$scope.zoom + "," + $scope.timeline.Robot[$scope.idx].Position._Y*$scope.zoom + " ";
            }
            $scope.last_idx = $scope.idx;
            $timeout($scope.refreshSVG, 1);

        }
        $scope.setRobotColor = function(id){

            if(id == 1){
                $scope.robotColor = 'img/svg/mickey_red_smile.svg';
            }
            if(id == 2){
                $scope.robotColor = 'img/svg/mickey_blue_smile.svg';
            }
            if(id == 3){
                $scope.robotColor = 'img/svg/mickey_green_smile.svg';
            }
        };

        $scope.setMazeColor = function(id){

            if(id == 1){
                $scope.groundColor = 'black';
                $scope.cheeseColor = 'img/svg/cheese.svg';
                $scope.circleBorder = '#00ffff';
                $scope.greatWallColor = '#008000';
                $scope.smallWallColor = '#0000ff';
                $scope.gridColor = '#cfd4db';

            }
            if(id == 2){
                $scope.groundColor = 'darkgrey';
                $scope.cheeseColor = 'img/svg/blackCheese.svg';
                $scope.circleBorder = '#cfd4db';
                $scope.greatWallColor = '#353535';
                $scope.smallWallColor = '#727272';
                $scope.gridColor = '#cfd4db';

            }

        };

        $scope.play = function() {
            if(!play){
                play = 1;
                refresh($scope.refresh_rate);
            }
        };

        $scope.pause = function(){
            if(play){
                play = 0;
                $timeout($scope.refreshSVG, 1);
            }
        };

        $scope.stop = function(){
            $scope.idx = 0;
            play = 0;
            refresh(0);
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
