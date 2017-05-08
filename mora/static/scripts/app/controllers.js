'use strict';
/* Common controllers */

angular.module('moApp.controllers', ['ngCookies','ui.router']).
	controller('moInitialize', ['sysLang', 'sysAuth', 'sysService',  '$rootScope', '$scope', 'loginFactory', 'sysFactory', '$location', '$modal', 'hotkeys', 'orgFactory', 'localStorageService', '$state', function (sysLang, sysAuth, sysService, $rootScope, $scope, loginFactory, sysFactory, $location, $modal, hotkeys, orgFactory, localStorageService, $state) {
		var _this = this; 
		_this.page; 
		_this.sysAuth = sysAuth;
		_this.sysService = sysService;
		$scope.isLoggedIn = sysAuth.getUserAuthentication(); // Check if user is authenticated
		$scope.authUserData = sysAuth.getUserData(); // Get logged in user data
		// Load common data
		if($scope.isLoggedIn){ sysService.loadData(); }
		$scope.$on('reloadTree', function(data){
			$scope.$broadcast('reloadTreeData', true);
		});
		$scope.$on('$stateChangeSuccess', function(event, toState, toParams, fromState, fromParams){
			// Store page keys
			sysService.state = toState;
			// Setup page variables
			$rootScope.page = toState.data.page;
			$rootScope.engagementOrgUnit = '';
			sysService.enableToolbar = true;
		});

		///////////////////////////////////////////////////////
		$scope.loginFailed = false;
		$scope.loginPopupOpened = false;
		$scope.logIn = function (section, state) {
			if(state == "open"){
				sysAuth.loginSection = section;
				if(sysAuth.getUserAuthentication()){ // User logged in
					if($scope.authUserData.rememberMe){ 
						if(sysAuth.loginSection == "emp"){ $location.path("/medarbejder"); 
						}else{ $location.path("/organisation"); }
					}else{
						localStorageService.clearAll();
						$scope.loginPopupOpened = true;
						$scope.loginPopupInstance = $modal.open({
						  templateUrl: sysService.path+'partials/login/login-popup.html',
						  controller: 'moHeaderLogin',
						  scope : $scope,
						  backdrop: 'static',
						  keyboard: false
						});
		  	    	}
				}else{
					$scope.loginPopupOpened = true;
					$scope.loginPopupInstance = $modal.open({
					  templateUrl: sysService.path+'partials/login/login-popup.html',
					  controller: 'moHeaderLogin',
					  scope : $scope,
					  backdrop: 'static',
					  keyboard: false
					});
				}
			}else if(state == "close"){
				$scope.loginPopupOpened = false;
				$scope.loginPopupInstance.dismiss('cancel');
			}
		};
		$scope.historyLogOpened = false;
		$scope.historyLog = function(state, url, title){
			if(state == "open"){
				$scope.historyLogOpened = true;
				$scope.historyLogModalInstance = $modal.open({
				  templateUrl: 'historyLog.html',
				  controller : 'moHistoryLog',
				  backdrop: 'static',
				  scope : $scope,
				  keyboard: false,
				  resolve: {
				  	historyUrl: function(){ return url; },
				  	historyTitle: function(){ return title; }
				  }
				});
			}else{
				$scope.historyLogModalInstance.dismiss('cancel');
				$scope.historyLogOpened = false;
			}
		}

		// Common application hotkeys
		hotkeys.add({
			combo: sysService.shortcuts.help.key,
			description: sysService.shortcuts.help.title,
			callback: function() {
				alert("Open help");
			}
		});
		hotkeys.add({
			combo: sysService.shortcuts.login.key,
			description: sysService.shortcuts.login.title,
			callback: function() {
				if(!$scope.loginPopupOpened){
					$scope.logIn('emp', 'open');
				}
			}
		});

	}])
	.controller('moHeader', ['$scope', '$rootScope', '$http', 'sysAuth','sysLang', '$location', 'sysFactory', 'sysService', 'localStorageService', '$filter', '$state', 'loginFactory', '$q', function ($scope, $rootScope, $http, sysAuth, sysLang, $location, sysFactory, sysService, localStorageService, $filter, $state, loginFactory, $q) {
		var _this = this;
		var stateParams = $state.params; 
		_this.sysService = sysService;
		_this.isLoggedIn = sysAuth.getUserAuthentication(); // Check if user is authenticated
		_this.authUserData = sysAuth.getUserData(); // Get logged in user data

	    _this.employeeSearch = new function(){
	    	var _this = this; 
	    	_this.cancelObj = {};
			_this.perform = function(obj){
				if(_this.cancelObj.hasOwnProperty('getSearchListEmp')){
					_this.cancelObj.getSearchListEmp.resolve();
				}
		    	var _formObj = obj;
		    	$location.path('medarbejder').search('query', obj.query);
		    };
		    _this.searchSelect = function(item, model, label){
				var searchMemory = []; var searchMemoryLen;
		    	if(localStorageService.get("searchedE")){
		    		searchMemory = localStorageService.get("searchedE");
		    	}else{ // Not exist
		    	}
				var index = _.detect(searchMemory, function (obj) {return obj.uuid === item.uuid});
				if(angular.isUndefined(index)){
			    	searchMemoryLen = searchMemory.length;
			    	item.order = (searchMemoryLen == 0)?100:searchMemoryLen+100;
				  	searchMemoryLen = (searchMemoryLen < 9)?"0"+(searchMemoryLen+1):(searchMemoryLen+1);
			    	searchMemory.push(item);
			    	localStorageService.set("searchedE", searchMemory);
			    }
		    	$location.path('medarbejder/'+item['user-key'])
		    }

			_this.getSearchList = function(val) {
				var canceler = $q.defer();				
				_this.cancelObj = {'getSearchListEmp' : canceler};				
				return $http.get('e', 
					{ params: { query: val, limit: 10, start: 0 },
					timeout: canceler.promise }
				).then(function(response){
					var resData = response.data;
					var x = 0;
					angular.forEach(resData, function(value, key){
						value.order = x;
						x++;
					}, resData);
			    	if(localStorageService.get("searchedE")){
			    		var searched = localStorageService.get("searchedE");
			    		var i = 100;
			    		angular.forEach(searched, function(value, key){
			    			var searchIn = _.find(resData,function(rw){ 
			    				if(rw.uuid == value.uuid) { 
			    					//resData = _.without(resData, rw);
			    				}
			    				return rw.uuid == value.uuid 
			    			});
			    			if(!angular.isDefined(searchIn) && !searchIn){
			    				value.order = i;
			    				resData.push(value);
			    				i++;
			    				sysService.recordEvent.set("debug","Found and Pushed ",value);
			    			}
			    		}, resData);
			    		resData = $filter('orderBy')(resData, 'order');
			  		}
			      	return resData;
			    });
		  	};
	    }

	    // Load org list
		if($scope.isLoggedIn){
			sysService.orgList.fetch().then(function(response){
				$scope.orgList = response;
			});
		}

		_this.orgSearch = new function(){
	    	var _this = this; 
	    	_this.cancelObj = {};

			_this.perform = function(obj){
				if(_this.cancelObj.hasOwnProperty('getSearchListOrg')){
					_this.cancelObj.getSearchListOrg.resolve();
				}
		    	var _formObj = obj;
		    	$location.path('organisation').search('query', obj.query);
		    };
		    _this.searchSelect = function(item, model, label){
				var searchMemory = []; var searchMemoryLen;
		    	if(localStorageService.get("searchedO")){
		    		searchMemory = localStorageService.get("searchedO");
		    	}else{ // Not exist
		    	}
				var index = _.detect(searchMemory, function (obj) {return obj.uuid === item.uuid});
				if(angular.isUndefined(index)){
			    	searchMemoryLen = searchMemory.length;
			    	item.order = (searchMemoryLen == 0)?100:searchMemoryLen+100;
				  	searchMemoryLen = (searchMemoryLen < 9)?"0"+(searchMemoryLen+1):(searchMemoryLen+1);
			    	searchMemory.push(item);
			    	localStorageService.set("searchedO", searchMemory);
			    }
		    	$location.path('organisation/'+item['uuid'])
		    }

			_this.getSearchList = function(val) {
				var canceler = $q.defer();
				_this.cancelObj = {'getSearchListOrg' : canceler};
				return $http.get('o/'+$scope.orgList[0].uuid+'/org-unit', 
					{ params: { query: val, limit: 10, start: 0 },
					timeout: canceler.promise }
				).then(function(response){
					var resData = response.data;
					var x = 0;
					angular.forEach(resData, function(value, key){
						value.order = x;
						x++;
					}, resData);
			    	if(localStorageService.get("searchedO")){
			    		var searched = localStorageService.get("searchedO");
			    		var i = 100;
			    		angular.forEach(searched, function(value, key){
			    			var searchIn = _.find(resData,function(rw){ 
			    				if(rw.uuid == value.uuid) { 
			    					//resData = _.without(resData, rw);
			    				}
			    				return rw.uuid == value.uuid 
			    			});
			    			if(!angular.isDefined(searchIn) && !searchIn){
			    				value.order = i;
			    				resData.push(value);
			    				i++;
			    				sysService.recordEvent.set("debug","Found and Pushed ",value);
			    			}
			    		}, resData);
			    		resData = $filter('orderBy')(resData, 'order');
			  		}
			      	return resData;
			    });
		  	};
	    }

	  	// Logout
		_this.logOut = function() {
   			loginFactory.out(_this.authUserData.authUser).then(function(response) {
   				sysAuth.unSetUserAuthentication(response.data);
   				$scope.$parent.isLoggedIn = false;
   				$scope.$parent.authUserData = {};
				$location.path("/");
			}, function(error){
				$location.path("/");
			});
	    };

	    _this.timeMachine = function(){
	    	window.open('#/timemachine', 'Resource', 'toolbar=no ,location=0, scrollbars=yes, status=no,titlebar=no,menubar=no,width='+screen.width +',height='+screen.height);
	    }
	    _this.appHelp = function(){
	    	window.open('#/help#org', 'Resource', 'toolbar=no ,location=0, scrollbars=yes, status=no,titlebar=no,menubar=no,width='+screen.width +',height='+screen.height);
	    }
	}])
	.controller('moFooter', ['$scope', '$http', 'sysAuth','sysLang', '$location', 'sysFactory', 'sysService', '$cookieStore', '$filter', 'sysLog', "$q", function ($scope, $http, sysAuth, sysLang, $location, sysFactory, sysService, $cookieStore, $filter, sysLog, $q) {
		sysLang = sysLang;
		$scope.language = sysLang.cookieLang;
		sysFactory.langs().then(function() {
	        var res = sysFactory.langsRes();
	        if(res.response){ // Success
	           $scope.langList = res.data;
			   sysLang.loadLang(); 
	        }
   		});
		$scope.updLang = function(){ sysLang.loadLang($scope.language); };
	}])
	.controller('moMain',['sysLang', 'sysAuth', '$rootScope', '$scope','$http', '$location', function (sysLang, sysAuth, $rootScope, $scope, $http, $location) {
	}])
	.controller('moHome', ['$scope', 'sysAuth','sysLang', '$modal', '$location', 'sysService', function ($scope, sysAuth, sysLang, $modal, $location, sysService) {
		//if(sysService.state.name == "home"){
			$scope.isLoggedIn = sysAuth.getUserAuthentication(); // Check if user is authenticated
			$scope.authUserData = sysAuth.getUserData(); // Get logged in user data
		//}
	}])
	.controller('moDashboard',['$scope', '$rootScope',function($scope, $rootScope){
	}])
	.controller('moOTreeSelecter',['$scope', '$rootScope',function($scope, $rootScope){
	}])
	.controller('moNotification',['$scope', 'sysFactory', 'sysService', 'hotkeys', function($scope, sysFactory, sysService, hotkeys){
		// Event list
		$scope.eventList = sysService.recordEvent.get();
	}])
	.controller('moHistoryLog',['$scope', 'sysFactory', 'sysService', 'hotkeys', 'historyUrl', 'historyTitle', function($scope, sysFactory, sysService, hotkeys, historyUrl, historyTitle){
		sysFactory.historyLog(historyUrl).then(function(res) {
			$scope.response = [];
            $scope.response.title = historyTitle;
            $scope.response.data = res;
        }, function(error){
        });

		hotkeys.add({
			combo: sysService.shortcuts.popupClose.key,
			description: sysService.shortcuts.popupClose.title,
			callback: function() {
				if($scope.historyLogOpened){ $scope.historyLog('close');}
			}
		});
	}])
	.controller('moErrorLog',['$scope', '$rootScope', '$modal',function($scope, $rootScope, $modal){
		$scope.logWin = function () {
			$scope.modalInstance = $modal.open({
			  templateUrl: 'errorLog.html',
			  scope : $scope,
			  backdrop: 'static',
			  keyboard: false
			});
		};
		$scope.cancel = function () {
			$scope.modalInstance.dismiss('cancel');
		};
		$scope.logWin();
	}]);