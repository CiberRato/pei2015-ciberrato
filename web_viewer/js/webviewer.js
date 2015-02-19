var x2js = new X2JS();
function convertXml2JSon() {
    return JSON.stringify(x2js.xml_str2json($("#labXML").val()));
}
function convertToStringPoints(cornerList, zoom){
    var out = "";
    var b = 0;
    for(; b<cornerList.Corner.length; b++){
        out+= cornerList.Corner[b]._X*zoom + "," + cornerList.Corner[b]._Y*zoom + " ";
    }
    return out;
}
angular.module('myapp', [])
    .controller('ctrl', ['$scope', function($scope){
        $scope.zoom = 30;


        var json_object = convertXml2JSon();
        var obj = angular.fromJson(json_object);
        for(i=0; i<obj.Lab.Wall.length; i++){
            obj.Lab.Wall[i].str = convertToStringPoints(obj.Lab.Wall[i], $scope.zoom);
        }
        console.log(obj.Lab);
        $scope.beacon_height = 2;
        $scope.map = obj.Lab;
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
    .directive('ngPoints', function() {
        return function(scope, element, attrs) {
            scope.$watch(attrs.ngPoints, function(value) {
                element.attr('points', value);
            });
        };
    });

angular.element(document).ready(function(){
    angular.bootstrap(document, ['myapp']);
});
