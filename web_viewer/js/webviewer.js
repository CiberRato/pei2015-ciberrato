var x2js = new X2JS();
function labConvertXml2JSon() {
    return JSON.stringify(x2js.xml_str2json($("#labXML").val()));
}
function gridConvertXml2JSon() {
    return JSON.stringify(x2js.xml_str2json($("#gridXML").val()));
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

        var grid_json_object = gridConvertXml2JSon();
        var grid_obj = angular.fromJson(grid_json_object);
        var lab_json_object = labConvertXml2JSon();
        var lab_obj = angular.fromJson(lab_json_object);

        for(i=0; i<lab_obj.Lab.Wall.length; i++){
            lab_obj.Lab.Wall[i].str = convertToStringPoints(lab_obj.Lab.Wall[i], $scope.zoom);
        }
        $scope.beacon_height = lab_obj.Lab.Beacon._Height;
        $scope.map = lab_obj.Lab;
        $scope.grid = grid_obj.Grid;
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
