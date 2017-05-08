'use strict';
/* Login page controllers */

var moApp = angular.module('moApp.controllers').
	controller('moLogin', ['$rootScope', '$scope','$http', '$location', '$filter', function ($rootScope, $scope, $http, $location, $filter) {
	}])
	.controller('moHeaderLogin', ['$scope', 'sysAuth', '$http', '$modal', '$location', 'loginFactory', 'sysService', 'hotkeys', 'localStorageService', function ($scope, sysAuth, $http, $modal, $location, loginFactory, sysService, hotkeys, localStorageService) {
	    $scope.moLoginProcess = function(){
	    	$scope.rememberme = (this.rememberme)?true:false;
	    	localStorageService.set("loginTimeStamp", new Date().getTime());

	    	/*if(!this.rememberme){	    		
			  	localStorageService.set("loginTimeStamp", new Date().getTime());
	      		window.onbeforeunload = function(e) {
	      			if(new Date().getTime() - localStorageService.get("loginTimeStamp") > 18000){
	  	    	  		localStorageService.clearAll();
	  	    	  		console.debug("Storage Erased....")
	  	    	  	} 
	  	    	};
	    	}*/

	    	$scope.loginBtnDisabled = true;
			$scope.$parent.loginFailed = false;
			
   			loginFactory.in(this.username, this.password, this.rememberme).then(function(response) { // Login success
   				$scope.loginBtnDisabled = false;
   				if(response.status == 200){ // Login success
   					var data = response.data;
   					loginFactory.acl().then(function(permission){
						permission =  _.filter(permission.data,function(rw){ return rw.role == data.role[0] });
   						sysAuth.setUserAuthentication(response.data, permission, $scope.rememberme);
	   					////////////////////////////////////////////////
	   					$scope.$parent.loginPopupOpened = false;
						$scope.$parent.loginFailed = false;
						$scope.$parent.isLoggedIn = true;
						$scope.$parent.authUserData = sysAuth.getUserData();
						///////////////////////////////////////////////
						$scope.$parent.loginPopupInstance.close();
						sysService.loadData();
						sysService.recordEvent.clean();
						if(sysAuth.loginSection == "emp"){ $location.path("/medarbejder"); 
						}else{ $location.path("/organisation"); }
						///////////////////////////////////////////////*/
   					})
   				}else{ // login failed
   					$scope.loginBtnDisabled = true;
   					$scope.$parent.loginFailed = true;
   				}
			}, function(error){ // Login failure
				$scope.$parent.loginFailed = true;
			});
	    };

		$scope.cancel = function () {
			$scope.$parent.loginFailed = false;
			$scope.$parent.loginPopupOpened = false;
			$scope.$parent.logIn('','close'); 
		};

		hotkeys.add({
			combo: sysService.shortcuts.popupClose.key,
			description: sysService.shortcuts.popupClose.title,
			callback: function() {
				if($scope.$parent.loginPopupOpened){ 
					$scope.$parent.loginFailed = false;
					$scope.$parent.loginPopupOpened = false;
					$scope.$parent.logIn('','close'); 
				}
			}
		});
		
	}]);