(function () {
    'use strict';

    angular.module('TofuApp', [])

    .controller('TofuController', ['$scope', '$log', '$http', '$timeout',
        function($scope, $log, $http, $timeout) {

            $scope.loading = {};

            $scope.stillRunning = function(recoId) {
                var timeout = "";
                var poller = function() {
                    $scope.loading['reco_' + recoId] = true;

                    // fire another request
                    $http.get('/reco/' + recoId + '/done').
                        success(function(data, status, headers, config) {
                            if(status === 202) {
                                $log.log(data, status);
                            } 
                            else if (status === 200) {
                                if (data.done) {
                                    $scope.loading['reco_' + recoId] = false;
                                    $log.log(data);
                                    $timeout.cancel(timeout);
                                    return false;
                                }
                            }
                            // continue to call the poller() function every 2 seconds
                            // until the timout is cancelled
                            timeout = $timeout(poller, 2000);
                        }).
                        error(function(error) {
                            $log.log(error);
                            $scope.loading = false;
                            $scope.submitButtonText = "Submit";
                            $scope.urlError = true;
                        });
                    };

                poller();
            };
        }
    ]);
}());
