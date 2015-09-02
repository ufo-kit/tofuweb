(function () {
    
    var show_hide_buttons_and_icons = function($scope, recoId, reco_flags) {
        // hide all buttons for current reco, but except delete button
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
        $scope.loading['reco_' + recoId + '_slice_map_creation_going' ] = true;
        $scope.loading['reco_' + recoId + '_slice_map_creation_with_error' ] = false;
        $scope.loading['reco_' + recoId + '_slice_map_creation_is_done' ] = false;

        // show icon "Slice_thumbs_creation_going"
        $scope.loading['reco_' + recoId + '_slices_thumbs_creation_going' ] = true;
        $scope.loading['reco_' + recoId + '_slices_thumbs_creation_with_error' ] = false;
        $scope.loading['reco_' + recoId + '_slices_thumbs_creation_is_done' ] = false;

        if(reco_flags['reco_done'] == true) {
            // show buttons open_info and load_slide
            $scope.loading['reco_' + recoId + '_open_info' ]   = false;
            $scope.loading['reco_' + recoId + '_load_slide' ]  = false;

            // show icon "reconstruction_is_done"
            $scope.loading['reco_' + recoId + '_reconstruction_going' ] = false;
            $scope.loading['reco_' + recoId + '_reconstruction_is_done' ] = true;
            $scope.loading['reco_' + recoId + '_reconstruction_with_error' ] = false;
        };

        if(reco_flags['reco_has_error'] == true) {
            // hide buttons open_info and load_slide
            $scope.loading['reco_' + recoId + '_open_info' ]   = true;
            $scope.loading['reco_' + recoId + '_load_slide' ]  = true;

            // show icon reconstruction_with_error
            $scope.loading['reco_' + recoId + '_reconstruction_going' ] = false;
            $scope.loading['reco_' + recoId + '_reconstruction_is_done' ] = false;
            $scope.loading['reco_' + recoId + '_reconstruction_with_error' ] = true;
        };

        if(reco_flags['slice_map_done'] == true) {
            // show button render
            $scope.loading['reco_' + recoId + '_render' ]      = false;

            // show icon slice_map_creation_is_done
            $scope.loading['reco_' + recoId + '_slice_map_creation_going' ] = false;
            $scope.loading['reco_' + recoId + '_slice_map_creation_is_done' ] = true;
            $scope.loading['reco_' + recoId + '_slice_map_creation_with_error' ] = false;
        };

        if(reco_flags['slice_map_has_error'] == true) {
            // hide button render
            $scope.loading['reco_' + recoId + '_render' ]      = true;

            // show icon slice_map_creation_with_error
            $scope.loading['reco_' + recoId + '_slice_map_creation_going' ] = false;
            $scope.loading['reco_' + recoId + '_slice_map_creation_is_done' ] = false;
            $scope.loading['reco_' + recoId + '_slice_map_creation_with_error' ] = true;
        };

        if(reco_flags['slices_thumbs_done'] == true) {
            // show button show_slides
            $scope.loading['reco_' + recoId + '_show_slides' ] = false;

            // show icon slices_thumbs_creation_is_done
            $scope.loading['reco_' + recoId + '_slices_thumbs_creation_going' ] = false;
            $scope.loading['reco_' + recoId + '_slices_thumbs_creation_is_done' ] = true;
            $scope.loading['reco_' + recoId + '_slices_thumbs_creation_with_error' ] = false;
        };

        if(reco_flags['slices_thumbs_has_error'] == true) {
            // hide icon show_slides
            $scope.loading['reco_' + recoId + '_show_slides' ] = true;

            // show icon slices_thumbs_creation_with_error
            $scope.loading['reco_' + recoId + '_slices_thumbs_creation_going' ] = false;
            $scope.loading['reco_' + recoId + '_slices_thumbs_creation_is_done' ] = false;
            $scope.loading['reco_' + recoId + '_slices_thumbs_creation_with_error' ] = true;
        };

    };

    angular.module('TofuApp', [])

    .controller('TofuController', ['$scope', '$log', '$http', '$timeout',
        function($scope, $log, $http, $timeout) {

            $scope.loading = {};

            $scope.recoStillRunning = function(recoId, reco_flags) {

                // console.log(recoId, reco_flags);

                var timeout = "";
                var poller = function() {
                    // fire another request
                    $http.get('/reco/' + recoId + '/done').
                        success(function(reco_flags, status, headers, config) {
                            // $log.log(reco_flags);
                            if(status === 202) {
                                $log.log(reco_flags, status);
                            } 
                            else if (status === 200) {
                                $log.log(reco_flags, status);

                                show_hide_buttons_and_icons($scope, recoId, reco_flags);

                                if(reco_flags['reco_done'] == true && reco_flags['slice_map_done'] == true && reco_flags['slices_thumbs_done'] == true) {
                                    // Stop requesting to /reco/ + recoId + /done. Timeout
                                    $timeout.cancel(timeout);
                                    return false;
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

                show_hide_buttons_and_icons($scope, recoId, reco_flags);

                if(reco_flags['reco_done'] != true || reco_flags['slice_map_done'] != true || reco_flags['slices_thumbs_done'] != true) {
                    // Start requesting to /reco/ + recoId + /done until timeout
                    poller();

                };

            };

        }
    ]);

}());