'use strict';
/* Employee controllers */

angular.module('moApp.controllers').
	controller('moOrgTree',["$scope", "$http", "$filter", "$state", "$rootScope", "$modal", "orgFactory", "$location", "sysService", "$q",function($scope, $http, $filter, $state, $rootScope, $modal, orgFactory, $location, sysService, $q) {
		$scope.organizations = [];
	  $scope.orgUnits = [];
      console.trace()
		// Load Orgs and OrgUnits
		sysService.orgList.fetch().then(function(response){
			$scope.organizations = response;
			sysService.loadOrgData.getUnits().then(function(response) {
	            $scope.orgUnits = response;
	        }, function(error){ // No child units
	        });
		});
	    // Tree Selection
    	$scope.selectNode = function(node){
			$location.path("organisation/"+node.uuid);
        };
	}])
	.controller('moOrgTreeInput',["$scope", "$http", "$filter", "$state", "$rootScope", "$modal", "orgFactory", "$location", "sysService", "$q", "$timeout",function($scope, $http, $filter, $state, $rootScope, $modal, orgFactory, $location, sysService, $q, $timeout) {
	  	$scope.node;
	  	$scope.orgList = [];
		$scope.orgUnit = [];
		$scope.$parent.treeDisabled = true;
		var date;
		
		// Load orgs ////////////////////////////////////////////////////////////
		$scope.orgList = function() {
	       sysService.orgList.get();
	    };        

	    $scope.$watch(function () {
	       sysService.orgList.data;
	    },                       
	    function(newVal, oldVal) {
	        $scope.orgList = sysService.orgList.data;
	    }, true);
	    ////////////////////////////////////////////////////////////////////
	    // Watch date change ///////////////////////////////////////////////
	    $scope.$parent.$watch('empObj.valid_from', function(newVal){
			if(angular.isDefined(newVal)){
				$scope.$parent.treeDisabled = false;
				date = $filter('date')(newVal, 'dd-MM-yyyy');
				$scope.query = "";
      			$scope.empCreateForm.$setPristine();
			}
		});
		////////////////////////////////////////////////////////////////////
	  	$scope.$on('orgUnitRowSelect', function(event, data) { 
	  		$scope.node = data;
	  	});

	    $scope.getOrgUnits = function (date, val, callback) {
	        var prom = [];
	        $scope.orgList.forEach(function (value, key){
	            prom.push(orgFactory.orgList(value.uuid, date, val).then(function(units) {
                    $scope.orgUnit[key] = [units.hierarchy];
                }));
	        });
	        $q.all(prom).then(function () {
	            callback();
	        });
	    };

		$scope.getOrgUnitInputTree = function(val) {
			var canceler = $q.defer();
			return $http.get('o/'+$scope.orgList[0].uuid+'/full-hierarchy', 
				{ params: { query: val, 'effective-date': date},
				timeout: canceler.promise }
			).then(function(response){
				var resData = response.data;
				return [resData.hierarchy];
			});
		}
		$scope.orgUnitSelect = function(item, model, label){
			item = $scope.node;
			model = $scope.node.name;
			$scope.$parent.empObj.org_unit = $scope.node;
			$scope.$emit('orgUnitSelected', $scope.node);
			return false;
		}
	}]).controller('moOrgMoveTreeInput',["$scope", "$http", "$filter", "$state", "$rootScope", "$modal", "orgFactory", "$location", "sysService", "$q", "$timeout",function($scope, $http, $filter, $state, $rootScope, $modal, orgFactory, $location, sysService, $q, $timeout) {
	  	$scope.node;
	  	$scope.orgList = [];
		$scope.orgUnit = [];
		$scope.moveString = "";
		$scope.$parent.treeDisabled = true;
		var date;

		
		// Load orgs ////////////////////////////////////////////////////////////
		$scope.orgList = function() {
	       sysService.orgList.get();
	    };        

	    $scope.$watch(function () {
	       sysService.orgList.data;
	    },                       
	    function(newVal, oldVal) {
	        $scope.orgList = sysService.orgList.data;
	    }, true);
	    ////////////////////////////////////////////////////////////////////	    

	    /*Custom watcher on date change in organisation move*/
		$scope.$parent.$watch('orgStartMoveDate', function(newVal){
			if(angular.isDefined(newVal)){
				$scope.$parent.treeDisabled = false;
				date = $filter('date')(newVal, 'dd-MM-yyyy');
				$scope.query = "";      			
			}
		});
		////////////////////////////////////////////////////////////////////
	  	$scope.$on('orgUnitRowSelect', function(event, data) { 
	  		$scope.node = data;
	  	});

	    $scope.getOrgUnits = function (date, val, callback) {
	        var prom = [];
	        $scope.orgList.forEach(function (value, key){
	            prom.push(orgFactory.orgList(value.uuid, date, val).then(function(units) {
                    $scope.orgUnit[key] = [units.hierarchy];
                }));
	        });
	        $q.all(prom).then(function () {
	            callback();
	        });
	    };

		$scope.getOrgUnitInputTree = function(val) {
			var canceler = $q.defer();
			return $http.get('o/'+$scope.orgList[0].uuid+'/full-hierarchy', 
				{ params: { query: val, 'effective-date': date},
				timeout: canceler.promise }
			).then(function(response){
				var resData = response.data;
				return [resData.hierarchy];
			});
		};
		$scope.orgUnitSelect = function(item, model, label){
			item = $scope.node;
			model = $scope.node.name;
			$scope.$parent.orgObj.org_unit = $scope.node;
			$scope.$parent.orgObj.moveString = $scope.moveString;
			$scope.$emit('orgMoveUnitSelected', $scope.$parent.orgObj);
			return false;
		}
	}]).controller('moOrgTreeInputField',["$scope", "$http", "$filter", "$state", "$rootScope", "$modal", "orgFactory", "$location", "sysService", "$q", "$timeout",function($scope, $http, $filter, $state, $rootScope, $modal, orgFactory, $location, sysService, $q, $timeout) {
	  	$scope.node;
	  	$scope.orgList = [];
		$scope.orgUnit = [];
		var date;

		// Load orgs ////////////////////////////////////////////////////////////
		$scope.orgList = function() {
	       sysService.orgList.get();
	    };        

	    $scope.$watch(function () {
	       sysService.orgList.data;
	    },                       
	    function(newVal, oldVal) {
	        $scope.orgList = sysService.orgList.data;
	    }, true);

	  	$scope.$on('orgUnitRowSelectField', function(event, data) { 
	  		$scope.node = data;
	  	});

	    $scope.getOrgUnits = function (date, val, callback) {
	        var prom = [];
	        $scope.orgList.forEach(function (value, key){
	            prom.push(orgFactory.orgList(value.uuid, date, val).then(function(units) {
                    $scope.orgUnit[key] = [units.hierarchy];
                }));
	        });
	        $q.all(prom).then(function () {
	            callback();
	        });
	    };

		$scope.getOrgUnitInputTree = function(val) {
			var canceler = $q.defer();
			return $http.get('o/'+$scope.orgList[0].uuid+'/full-hierarchy', 
				{ params: { query: val, 'effective-date': date},
				timeout: canceler.promise }
			).then(function(response){
				var resData = response.data;
				return [resData.hierarchy];
			});
		}
		$scope.orgUnitSelect = function(item, model, label){
			item = $scope.node;
			model = $scope.node.name;
			if($scope.type=="toEmp"){
				$scope.$parent.original_org_unit = $scope.node;
			}else{
				$scope.$parent.org_unit = $scope.node;	
			}
			
			return false;
		}
	}]).controller('moOrgTreeInputField2',["$scope", "$http", "$filter", "$state", "$rootScope", "$modal", "orgFactory", "$location", "sysService", "$q", "$timeout",function($scope, $http, $filter, $state, $rootScope, $modal, orgFactory, $location, sysService, $q, $timeout) {
	  	
	/* =================================

NOTE: Dupliocate of 'moOrgTreeInputField' directive.
Only change is to allow 2nd Org Unit Selector to function 
within same controller scope. Change made in orgUnitSelect()

	================================= */

	  	$scope.node;
	  	$scope.orgList = [];
		$scope.orgUnit = [];
		var date;

		// Load orgs ////////////////////////////////////////////////////////////
		$scope.orgList = function() {
	       sysService.orgList.get();
	    };        

	    $scope.$watch(function () {
	       sysService.orgList.data;
	    },                       
	    function(newVal, oldVal) {
	        $scope.orgList = sysService.orgList.data;
	    }, true);

	  	$scope.$on('orgUnitRowSelectField', function(event, data) { 
	  		$scope.node = data;
	  	});

	    $scope.getOrgUnits = function (date, val, callback) {
	        var prom = [];
	        $scope.orgList.forEach(function (value, key){
	            prom.push(orgFactory.orgList(value.uuid, date, val).then(function(units) {
                    $scope.orgUnit[key] = [units.hierarchy];
                }));
	        });
	        $q.all(prom).then(function () {
	            callback();
	        });
	    };

		$scope.getOrgUnitInputTree = function(val) {
			var canceler = $q.defer();
			return $http.get('o/'+$scope.orgList[0].uuid+'/full-hierarchy', 
				{ params: { query: val, 'effective-date': date},
				timeout: canceler.promise }
			).then(function(response){
				var resData = response.data;
				return [resData.hierarchy];
			});
		}
		$scope.orgUnitSelect = function(item, model, label){
			item = $scope.node;
			model = $scope.node.name;

			//$scope.$parent.$parent.org_unit = $scope.node;
			$scope.$parent.$parent.original_org_unit = $scope.node;
			return false;
		}
	}]);
