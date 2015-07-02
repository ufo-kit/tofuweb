(function () {
    'use strict';

    angular.module('TofuApp', [])

    .controller('TofuController', ['$scope', '$log', '$http', '$timeout',
        function($scope, $log, $http, $timeout) {

            $scope.loading = {};

            $scope.recoStillRunning = function(recoId, reco_flags) {

                console.log(recoId, reco_flags);

                var timeout = "";
                var poller = function() {
                    // fire another request
                    $http.get('/reco/' + recoId + '/done').
                        success(function(data, status, headers, config) {
                            // $log.log(data);
                            if(status === 202) {
                                $log.log(data, status);
                            } 
                            else if (status === 200) {
                                if (data.reco_done) {
                                    if(data.reco_has_error == false) {
                                        $scope.loading['reco_' + recoId + '_open_info' ] = false;
                                        $scope.loading['reco_' + recoId + '_load_slide' ] = false;

                                        // show icon "Reconstruction_is_done"
                                        $scope.loading['reco_' + recoId + '_reconstruction_going' ] = false;
                                        $scope.loading['reco_' + recoId + '_reconstruction_is_done' ] = true;
                                        $scope.loading['reco_' + recoId + '_reconstruction_with_error' ] = false;

                                    } else {
                                        // show icon "Reconstruction_with_error"
                                        $scope.loading['reco_' + recoId + '_reconstruction_going' ] = false;
                                        $scope.loading['reco_' + recoId + '_reconstruction_is_done' ] = false;
                                        $scope.loading['reco_' + recoId + '_reconstruction_with_error' ] = true;

                                    };

                                    if (data.slice_map_done) {
                                        if(data.slice_map_has_error == false) {
                                            $scope.loading['reco_' + recoId + '_render' ] = false;
                                            
                                            // show icon "Slice_map_creation_is_done"
                                            $scope.loading['reco_' + recoId + '_slice_map_creation_going' ] = false;
                                            $scope.loading['reco_' + recoId + '_slice_map_creation_is_done' ] = true;
                                            $scope.loading['reco_' + recoId + '_slice_map_creation_with_error' ] = false;
    
                                        } else {
                                            // show icon "Slice_map_creation_with_error"
                                            $scope.loading['reco_' + recoId + '_slice_map_creation_going' ] = false;
                                            $scope.loading['reco_' + recoId + '_slice_map_creation_is_done' ] = false;
                                            $scope.loading['reco_' + recoId + '_slice_map_creation_with_error' ] = true;

                                        };

                                        if (data.slices_thumbs_done) {
                                            if(data.slices_thumbs_has_error == false) {
                                                $scope.loading['reco_' + recoId + '_show_slides' ] = false;
                                                
                                                // show icon "Slice_map_creation_is_done"
                                                $scope.loading['reco_' + recoId + '_slices_thumbs_creation_going' ] = false;
                                                $scope.loading['reco_' + recoId + '_slices_thumbs_creation_is_done' ] = true;
                                                $scope.loading['reco_' + recoId + '_slices_thumbs_creation_with_error' ] = false;
                                        
                                            } else {
                                                // show icon "Slice_map_creation_with_error"
                                                $scope.loading['reco_' + recoId + '_slices_thumbs_creation_going' ] = false;
                                                $scope.loading['reco_' + recoId + '_slices_thumbs_creation_is_done' ] = false;
                                                $scope.loading['reco_' + recoId + '_slices_thumbs_creation_with_error' ] = true;

                                            };

                                            $timeout.cancel(timeout);
                                            return false;
                                        }
                                    }
                                }
                            };
                            // continue to call the poller() function every 2 seconds
                            // until the timout is cancelled
                            timeout = $timeout(poller, 1000);
                        }).
                        error(function(error) {
                            $log.log(error);
                            $scope.loading = false;
                            $scope.submitButtonText = "Submit";
                            $scope.urlError = true;
                        });
                };

                $scope.loading['reco_' + recoId + '_show_slides' ] = true;
                $scope.loading['reco_' + recoId + '_render' ]      = true;
                $scope.loading['reco_' + recoId + '_open_info' ]   = true;
                $scope.loading['reco_' + recoId + '_load_slide' ]  = true;
                $scope.loading['reco_' + recoId + '_delete' ]      = false;

                // show icon "Reconstruction_going"
                $scope.loading['reco_' + recoId + '_reconstruction_going' ] = true;
                $scope.loading['reco_' + recoId + '_reconstruction_is_done' ] = false;
                $scope.loading['reco_' + recoId + '_reconstruction_with_error' ] = false;

                // show icon "Slice_map_creation_going"
                $scope.loading['reco_' + recoId + '_slice_map_creation_with_error' ] = false;
                $scope.loading['reco_' + recoId + '_slice_map_creation_is_done' ] = false;
                $scope.loading['reco_' + recoId + '_slice_map_creation_going' ] = true;

                // show icon "Slice_thumbs_creation_going"
                $scope.loading['reco_' + recoId + '_slices_thumbs_creation_with_error' ] = false;
                $scope.loading['reco_' + recoId + '_slices_thumbs_creation_is_done' ] = false;
                $scope.loading['reco_' + recoId + '_slices_thumbs_creation_going' ] = true;
                
                
                if(reco_flags['reco_done'] == true || reco_flags['slice_map_done'] == true) {
                    if(reco_flags['reco_has_error'] == false) {
                        $scope.loading['reco_' + recoId + '_open_info' ] = false;
                        $scope.loading['reco_' + recoId + '_load_slide' ] = false;

                        // show icon "Reconstruction_is_done"
                        $scope.loading['reco_' + recoId + '_reconstruction_going' ] = false;
                        $scope.loading['reco_' + recoId + '_reconstruction_is_done' ] = true;
                        $scope.loading['reco_' + recoId + '_reconstruction_with_error' ] = false;


                    } else {
                        // show icon "Reconstruction_with_error"
                        $scope.loading['reco_' + recoId + '_reconstruction_going' ] = false;
                        $scope.loading['reco_' + recoId + '_reconstruction_is_done' ] = false;
                        $scope.loading['reco_' + recoId + '_reconstruction_with_error' ] = true;

                    };

                    if(reco_flags['slice_map_has_error'] == false) {
                        $scope.loading['reco_' + recoId + '_render' ] = false;

                        // show icon "Slice_map_creation_is_done"
                        $scope.loading['reco_' + recoId + '_slice_map_creation_going' ] = false;
                        $scope.loading['reco_' + recoId + '_slice_map_creation_is_done' ] = true;
                        $scope.loading['reco_' + recoId + '_slice_map_creation_with_error' ] = false;


                    } else {
                        // show icon "Slice_map_creation_with_error"
                        $scope.loading['reco_' + recoId + '_slice_map_creation_going' ] = false;
                        $scope.loading['reco_' + recoId + '_slice_map_creation_is_done' ] = false;
                        $scope.loading['reco_' + recoId + '_slice_map_creation_with_error' ] = true;

                    };

                    if(reco_flags['slices_thumbs_has_error'] == false) {
                        $scope.loading['reco_' + recoId + '_show_slides' ] = false;

                        // show icon "Slices_thumbs_creation_is_done"
                        $scope.loading['reco_' + recoId + '_slices_thumbs_creation_going' ] = false;
                        $scope.loading['reco_' + recoId + '_slices_thumbs_creation_is_done' ] = true;
                        $scope.loading['reco_' + recoId + '_slices_thumbs_creation_with_error' ] = false;


                    } else {
                        // show icon "Slices_thumbs_creation_with_error"
                        $scope.loading['reco_' + recoId + '_slices_thumbs_creation_going' ] = false;
                        $scope.loading['reco_' + recoId + '_slices_thumbs_creation_is_done' ] = false;
                        $scope.loading['reco_' + recoId + '_slices_thumbs_creation_with_error' ] = true;

                    };

                } else {
                    poller();

                };

            };

        }
    ]);

}());