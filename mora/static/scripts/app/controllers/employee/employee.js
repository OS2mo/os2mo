'use strict';
/* Employee controllers */

angular.module('moApp.controllers').
	  controller('moEmployee',["$scope", "$http", "$filter", "$state", "$rootScope", "$modal", "empFactory", "$location", "$timeout", "ngTableParams", "sysService", "$q",function($scope, $http, $filter, $state, $rootScope, $modal, empFactory, $location, $timeout, ngTableParams, sysService, $q) {
	  }])	 
	  .controller('moEmployeeList',["$scope", "$http", "$filter", "$state", "$rootScope", "$modal", "empFactory", "$location", "$timeout", "ngTableParams", "sysService", "$q",function($scope, $http, $filter, $state, $rootScope, $modal, empFactory, $location, $timeout, ngTableParams, sysService, $q) {
	  	var _this = this;
	  	var searchParam = "";
		var stateParams = $state.params; 
		if(angular.isDefined(stateParams) && angular.isDefined(stateParams.query) && stateParams.query !== null){  $scope.queryString = stateParams.query; }
		$scope.employeesFound;
		$scope.employeesLoaded = false;
		if(angular.isDefined($scope.queryString)){
		    $scope.employees = new ngTableParams({
		        page: 1,    // show first page
		        count: 200,  // count per page
		        limit:10,	// Limit per page
		        start: 0	// Start from
		    }, {
		        total: 0,           // length of data
		        getData: function($defer, params) {
		        	var customParam = {
		        		"limit": params.count(),
		        		"start": (params.page()-1)*params.$params.limit,
		        		"query": $scope.queryString
		        	};
		            $http.get("e/", {"params": customParam }).then(
	            		function(response){ 
	            			$scope.employeesFound = true;
	            			$scope.employeesLoaded = true;
	            			$timeout(function() {
	            				params.total(40);
	            				$defer.resolve(response.data);
	            			},500);
	            		},
	                	function(error){
	                		$scope.employeesFound = false; 
	                		$scope.employeesLoaded = true;
	                		return $q.reject(error); }
	                );
		        }
		    });
		}
	  }])
	  .controller('moEmployeeMaster',["$scope", "$http", "$filter", "$state", "$rootScope", "$modal", 'empFactory', "$q", "$location", "sysService", "hotkeys", "$timeout", function($scope, $http, $filter, $state, $rootScope, $modal, empFactory, $q, $location, sysService, hotkeys, $timeout) {

	  	$scope.flag = {
	  		empFound: false,
	  		empInfoLoaded: false,
	  		empEngagementsFound: false,
	  		empEngagementsLoaded: false,
	  		empEdit: false,
	  		empEditSuccess: false,
	  		empCreate: false,
	  		empCreateSuccess: false,
	  		dataUpdated: false,
	  		dataUnsaved: false
	  	};
	  	$scope.empCPR;
	  	$scope.visibleEngagementCount = 0;
	  	$scope.validity = ['present', 'past', 'future'];
		$scope.engagements = {
			"engagement":{ "key": "engagement", "visible":false}, // Editable
			"association":{"key": "association", "visible":false}, // Editable
			"it":{"key": "it", "visible":false}, // Editable
			"contact":{"key": "contact", "visible":false}, // Editable
			"job-function":{"key": "job-function", "visible":false}, // Editable
			"leader":{"key": "leader", "visible":false}, // Editable
			"absence":{"key": "absence", "visible":false} // Editable
        };
        var active = false;
        ////////////////////////////////////////////////////////////////////////////////////
  		
	  	$scope.empEndModalOpen = false;
		$scope.empEndModal = function (state){
			if(state == "open"){
				$scope.empEndModalOpen = true;
				$scope.empEndInstance = $modal.open({
				  templateUrl: sysService.path+'partials/employee/employeeEnd.html',
				  controller: 'employeeEnd',
				  scope : $scope,
				  backdrop: 'static',
				  keyboard: false,
				  windowClass: 'employeeEnd'
				});
			}else if(state == "close"){
				$scope.empEndModalOpen = false;
				$scope.empEndInstance.dismiss('cancel');
			}
		};
		
		$scope.empAbsenceModalOpen = false;
		$scope.empAbsenceModal = function (state){
			if(state == "open"){
				$scope.empAbsenceModalOpen = true;
				$scope.empAbsenceInstance = $modal.open({
				  templateUrl: sysService.path+'partials/employee/employeeAbsence.html',
				  controller: 'employeeAbsence',
				  scope : $scope,
				  backdrop: 'static',
				  keyboard: false,
				  windowClass: 'employeeAbsence'
				});
			}else if(state == "close"){
				$scope.empAbsenceModalOpen = false;
				$scope.empAbsenceInstance.dismiss('cancel');
			}
		};
		
		$scope.empNewModalOpen = false;
		$scope.sysService = sysService;
		$scope.empNewModal = function (state){
			if(state == "open"){
				$scope.empNewModalOpen = true;
				$scope.empNewInstance = $modal.open({
				  templateUrl: sysService.path+'partials/employee/employeeNew.html',
				  controller: 'employeeNew',
				  scope : $scope,
				  backdrop: 'static',
				  keyboard: false,
				  windowClass: 'employeeNew'
				});
			}else if(state == "close"){
				$scope.empNewModalOpen = false;
				$scope.empNewInstance.dismiss('cancel');
			}
		};
		
		$scope.empMoveModalOpen = false;
		$scope.empMoveModal = function (state){
			if(state == "open"){
				$scope.empMoveModalOpen = true;
				$scope.empMoveInstance = $modal.open({
				  templateUrl: sysService.path+'partials/employee/employeeMove.html',
				  controller: 'employeeMove',
				  scope : $scope,
				  backdrop: 'static',
				  keyboard: false,
				  windowClass: 'employeeMove'
				});
			}else if(state == "close"){
				$scope.empMoveModalOpen = false;
				$scope.empMoveInstance.dismiss('cancel');
			}
		};
		
		$scope.empMoveManyModalOpen = false;
		$scope.empMoveManyModal = function (state){
			if(state == "open"){
				$scope.empMoveManyModalOpen = true;
				$scope.empMoveManyInstance = $modal.open({
				  templateUrl: sysService.path+'partials/employee/employeeMoveMany.html',
				  controller: 'employeeMoveMany',
				  scope : $scope,
				  backdrop: 'static',
				  keyboard: false,
				  windowClass: 'employeeMoveMany'
				});
			}else if(state == "close"){
				$scope.empMoveManyModalOpen = false;
				$scope.empMoveManyInstance.dismiss('cancel');
			}
		};

		$scope.empViewOpen = false;
		$scope.empView = function (state, userkey){
			if(state == "open"){
				if(angular.isDefined(userkey) && userkey != ""){ 
					$scope.flag.empFound = false;
	  				$scope.flag.empInfoLoaded = false;
	  				$scope.flag.empEngagementsFound = false;
	  				$scope.employee = {};
					$scope.cleanUpEmpData();
				}				
				$scope.empViewInstance = $modal.open({
				  templateUrl: sysService.path+'partials/employee/employeeViewEdit.html',
				  controller: 'employeeViewEdit',
				  scope : $scope,
				  backdrop: 'static',
				  keyboard: false,
				  windowClass: 'employeeViewEdit'
				});
				$scope.empViewInstance.opened.then(function() {
					$timeout(function(){
						$scope.empViewOpen = true;
						$scope.flag.empEdit = false;
						$scope.flag.empCreate = false;
						if(angular.isDefined(userkey) && userkey != ""){
							empFactory.empHeaders().then(function(response) {
								$scope.cleanUpEmpData();
								$scope.tables = response;
								$scope.initEmpData(userkey);
							});
						}
					}, 2000); 
				});
			}else if(state == "close"){
				$scope.empViewOpen = false;
				$scope.flag.empEdit = false;
				$scope.flag.empCreate = false;
				if(angular.isDefined($scope.empViewInstance))
					$scope.empViewInstance.dismiss('cancel');
				if(angular.isDefined($scope.empEditInstance))
					$scope.empEditInstance.dismiss('cancel');
			}
		};

		$scope.empEditOpen = false;
		$scope.empEdit = function (state, userkey){
			if(state == "open"){
				if(angular.isDefined(userkey) && userkey != ""){ 
					$scope.flag.empFound = false;
					$scope.flag.empInfoLoaded = false;
					$scope.flag.empEngagementsFound = false;
					$scope.employee = {};
					$scope.cleanUpEmpData();
				}				
				$scope.empEditInstance = $modal.open({
				  templateUrl: sysService.path+'partials/employee/employeeViewEdit.html',
				  controller: 'employeeViewEdit',
				  scope : $scope,
				  backdrop: 'static',
				  keyboard: false,
				  windowClass: 'employeeViewEdit'
				});
				$scope.empEditInstance.opened.then(function() {
					$timeout(function(){
						$scope.empEditOpen = true;
						$scope.flag.empEdit = true;
						$scope.flag.empCreate = true;
						if(angular.isDefined(userkey) && userkey != ""){
							empFactory.empHeaders().then(function(response) {
								$scope.cleanUpEmpData();
								$scope.tables = response;
								$scope.initEmpData(userkey);
							});
						}
					}, 2000); 
				});
			}else if(state == "close"){
				$scope.empEditOpen = false;
				$scope.flag.empEdit = false;
				$scope.flag.empCreate = false;
				if($scope.flag.dataUnsaved){
					if(sysService.state.data.page.key == "employee" && sysService.state.data.page.subKey == "detail"){
						$scope.initEmpData();
					}
					$scope.flag.dataUnsaved=false;
				}
				if(angular.isDefined($scope.empViewInstance))
					$scope.empViewInstance.dismiss('cancel');
				if(angular.isDefined($scope.empEditInstance))
					$scope.empEditInstance.dismiss('cancel');
			}
		};

		$scope.resetViewEdit = function(){
			$scope.$emit('resetViewEdit');
		}
		// Hotkeys for workflow actions
		hotkeys.add({
			combo: sysService.shortcuts.employeeWorkflowEnd.key,
			description: sysService.shortcuts.employeeWorkflowEnd.title,
			callback: function() {
				if(!$scope.empEndModalOpen && (sysService.setupACL.validate('e|write'))){
					$scope.empEndModal('open');
				}
			}
		});

		hotkeys.add({
			combo: sysService.shortcuts.employeeWorkflowAbsence.key,
			description: sysService.shortcuts.employeeWorkflowAbsence.title,
			callback: function() {
				if(!$scope.empAbsenceModalOpen && (sysService.setupACL.validate('e|write'))){
					$scope.empAbsenceModal('open');
				}
			}
		});

		hotkeys.add({
			combo: sysService.shortcuts.employeeWorkflowNew.key,
			description: sysService.shortcuts.employeeWorkflowNew.title,
			callback: function() {
				if(!$scope.empNewModalOpen && (sysService.setupACL.validate('e|write'))){
					$scope.empNewModal('open');
				}
			}
		});

		hotkeys.add({
			combo: sysService.shortcuts.employeeWorkflowMove.key,
			description: sysService.shortcuts.employeeWorkflowMove.title,
			callback: function() {
				if(!$scope.empMoveModalOpen && (sysService.setupACL.validate('e|write'))){
					$scope.empMoveModal('open');
				}
			}
		});

		hotkeys.add({
			combo: sysService.shortcuts.employeeWorkflowMoveMany.key,
			description: sysService.shortcuts.employeeWorkflowMoveMany.title,
			callback: function() {
				if(!$scope.empMoveManyModalOpen && (sysService.setupACL.validate('e|write'))){
					$scope.empMoveManyModal('open');
				}
			}
		});

		////////////////////////////////////////////////////////////////////////////////
		$scope.initEmpData = function (cpr){
			cpr = (angular.isDefined(cpr) && cpr != "")?cpr:$scope.empCPR;
			empFactory.empInfosByCPR(cpr).then(function(response){
				var empUUID = response["uuid"]; 
				$scope.employee = response;
				$scope.empCPR = response["user-key"]; 
				$scope.empUUID = response["uuid"]; 
				$scope.visibleEngagementsCount = 0;
				$scope.flag.empFound = true;
				$scope.flag.empInfoLoaded = true;
				active = false;
				angular.forEach($scope.engagements, function(role, key){
					$scope.loadEngagements(empUUID, key);
				});
			}, function(error){
				$scope.flag.empFound = false;
				$scope.flag.empInfoLoaded = true;
			});
		};

		$scope.cleanUpEmpData = function(){
			angular.forEach($scope.tables, function(row, key){
				angular.forEach($scope.engagements, function(role, key){
					row.tr[role] = [];
				});
			});
			angular.forEach($scope.engagements, function(role, key){
				role.visible = false;
				angular.forEach($scope.validity, function(validity, position){
					role[validity] = false;
				});
			})
		};

		sysService.orgList.fetch().then(function(response){
			$scope.organizations = response;
		});

		var activeEngagement = false;
		$scope.loadEngagements = function(cpr, engagement){
			var prom = [];
			var table = $scope.tables[engagement];
			var defaultTab = '';
			var visible = false;
			var treeSet = false;

			$scope.engagements[engagement].errorCreate = false;
			$scope.engagements[engagement].errorUpdate = false;
			$scope.engagements[engagement].changed = false;
			$scope.engagements[engagement].added = false;
			
			$scope.engagements[engagement]['visible'] = visible;
			angular.forEach($scope.validity, function(validity, position){
				table.tr[validity] = [];

				$scope.engagements[engagement][validity] = false; 
				prom.push(empFactory.empRoles(cpr, engagement, '', validity).then(function(response){
					if(validity == "present" && engagement == "it"){
						if(response[0]['it-system'].name == "Odknet"){
							$scope.odknet_name = response[0]['user-name'];
						}
					}
					table.tr[validity] = [];
					table.tr[validity] = response;
					if(response.length > 0){
						$scope.engagements[engagement].timeStamp = _.now();
						// Set default tab
						if(engagement == 'engagement'){ $scope.engagements[engagement].active = true;}
						if(!activeEngagement){ activeEngagement = true;}
						// Set default according option
						$scope.engagements[engagement][validity] = true;
						// Count for tab shortcut
						$scope.engagements[engagement]['display'] = true;
					}
				},function(error){
				}));
			});
			$q.all(prom).then(function (result) {
				var role = $scope.engagements[engagement];
				if(role.display){
					var defaultTabSet = false;
					angular.forEach($scope.validity, function(validity, position){
						if(role[validity] && !defaultTabSet){
							role.defaultTab = 'present';//validity;
							defaultTabSet = true;
							$scope.flag.empEngagementsFound = true;
						}
						if(validity == 'present' && !treeSet && sysService.state.data.page.key == "employee" && sysService.state.data.page.subKey == "detail"){
							treeSet = true;
							//$scope.setTreeTab(table.tr[validity][0]);
						}
					});
					$scope.engagements[engagement]['visible'] = true;
					$scope.visibleEngagementsCount++;
				}
			});
		};

		/*$scope.$on('$stateChangeSuccess', function(event, toState, toParams, fromState, fromParams){
			$scope.setTreeTab([]);
		});*/

		/*$scope.setTreeTab = function(row){
			if(angular.isDefined(row['org-unit']) && row['org-unit'].name != ""){
				$scope.$parent.selectedOrgUnit = {
					'node': row['org-unit'],
					'org-unit': $scope.organizations[0].uuid
				};
			}else{
				$scope.$parent.selectedOrgUnit = {
					'node': undefined,
					'org-unit': $scope.organizations[0].uuid
				};
			}
		};*/

	  }])
	.controller('moEmployeeDetail',["$scope", "$http", "$state", "$modal", 'empFactory', "$q", "$location", "sysService", "hotkeys", function($scope, $http, $state, $modal, empFactory, $q, $location, sysService, hotkeys) {
			$scope.sysService = sysService;
		var _loadEmpDetails = function(cpr, date){
			$scope.$parent.empInfoLoaded = false;
	        empFactory.empHeaders().then(function(response) {
				$scope.$parent.cleanUpEmpData();
				$scope.$parent.tables = response;
				$scope.$parent.initEmpData(cpr);
			});
		}

		$scope.setOrgUnit = function(role, dataRow){
			if(role.present){
				var row = dataRow['present'][0];
				//$scope.$parent.setTreeTab(row);
			}
		}
		/////////////////////////////////////////////////////////////////
		var stateParams = $state.params;
		if(stateParams && stateParams.cpr){ // If URL have UUID/User-Key
			_loadEmpDetails(stateParams.cpr);

			hotkeys.add({
				combo: sysService.shortcuts.employeeView.key,
				description: sysService.shortcuts.employeeView.title,
				callback: function() {
					if(!$scope.$parent.empViewOpen){
						$scope.$parent.empView('open');
					}
				}
			});

			hotkeys.add({
				combo: sysService.shortcuts.employeeEdit.key,
				description: sysService.shortcuts.employeeEdit.title,
				callback: function() {
					if(!$scope.$parent.empEditOpen && (sysService.setupACL.validate('e|write'))){
						$scope.$parent.empEdit('open');
					}
				}
			});

			$scope.$parent.$watch("visibleEngagementsCount", function(newVal){
				if(angular.isDefined(newVal) && newVal > 0){
					angular.forEach($scope.$parent.engagements, function(value, index){
						if(value.visible){
							hotkeys.add({
								combo: "alt+"+newVal,
								description: 'Switch tab',
								callback: function() {
									$scope.$parent.engagements[index].active = true
								}
							});
						}
					})
				}
			});
		}
	}])  
	.controller('employeeViewEdit',["$scope", "$http", "$filter", "$state", "$rootScope", "$modal", "sysService", "empFactory", "$q", "hotkeys", "$timeout",function($scope, $http, $filter, $state, $rootScope, $modal, sysService, empFactory, $q, hotkeys, $timeout) {
		$scope.$on('resetViewEdit', function(event, data){
			$scope.editEmployeeFunc.resetViewEdit();
		});
		$scope.sysService = sysService;
		$scope.inlineDatePicker = {'from': false, 'to': false};
		$scope.openInlineDatePicker = function($event, cal) {
			$event.preventDefault();
			$event.stopPropagation();
			angular.forEach($scope.inlineDatePicker, function(value, key){
				if(key != cal){ $scope.inlineDatePicker[key] = false; }
			});
			$scope.inlineDatePicker[cal] = ($scope.inlineDatePicker[cal])?false:true;
		};
		$scope.closeInlineDatePicker = function() {
			angular.forEach($scope.inlineDatePicker, function(value, key){
				$scope.inlineDatePicker[key] = false;
			});
		};
		// Load Orgs and OrgUnits
		sysService.orgList.fetch().then(function(response){
			$scope.organizations = response;
		});
  		// Edit Employee Function //////////
  		////////////////////////////////////
  		$scope.editEmployeeFunc = {
			updatedData : {
				"engagement":{},
				"association":{},
				"it":{},
				"contact":{},
				"job-function":{},
				"leader":{},
				"absence":{}
        	},
        	opened : false,
        	datePicker: function(state){
        		if(state == "open"){
        			$scope.editOrganisationFunc.opened = true;
        		}else{
        			$scope.editOrganisationFunc.opened = false;
        		}
        	},
        	resetViewEdit: function(){
        		angular.forEach($scope.editEmployeeFunc.updatedData, function(value, index){
					value = {};
				});
        	},
			validationError : [],
			formatDate : function(strVal) {
    			strVal = $filter('date')(strVal, 'dd-MM-yyyy');
    		    return strVal;
		  	},
		  	jobTitles: {},
			jobTitle : function(str, role) {
				var _this = this;
				if(!angular.isDefined(role)){
	    			return _this.jobTitles.length ? null : $http.get('role-types/engagement/facets/job-title/classes/').success(function(response) {
	      				_this.jobTitles = response;
	    			});
    			}else{
					if(angular.isDefined(str) && _this.jobTitles && _this.jobTitles.length) {
						var selected = $filter('filter')(_this.jobTitles, {uuid: str.uuid});
						return selected.length ? selected[0].name : '---'; /* Not set */
					} else {
						if(angular.isDefined(str)){
							return str.name || '---'; /* Not set */
						}else{
							return '---'; /* Not set */
						}
					}
    			}
  			},
  			empTypes: {},
			empType : function(str, role) {
				var _this = this;
				if(!angular.isDefined(role)){
	    			return _this.empTypes.length ? null : $http.get('role-types/engagement/facets/type/classes/').success(function(response) {
	      				_this.empTypes = response;
	    			});
    			}else{
    				if(angular.isDefined(str) && _this.empTypes && _this.empTypes.length) {
						var selected = $filter('filter')(_this.empTypes, {uuid: str.uuid});
						return selected.length ? selected[0].name : '---'; /* Not set */
					} else {
						if(angular.isDefined(str)){
							return str.name || '---'; /* Not set */
						}else{
							return '---'; /* Not set */
						}
					}
    			}
  			},
			leaderTitles: {},
			leaderTitle : function(str, role) {
				var _this = this;
				if(!angular.isDefined(role)){
	    			return _this.leaderTitles.length ? null : $http.get('role-types/leader/facets/title/classes/').success(function(response) {
	      				_this.leaderTitles = response;
	    			});
    			}else{
					if(angular.isDefined(str) && _this.leaderTitles && _this.leaderTitles.length) {
						var selected = $filter('filter')(_this.leaderTitles, {uuid: str.uuid});
						return selected.length ? selected[0].name : '---'; /* Not set */
					} else {
						if(angular.isDefined(str)){
							return str.name || '---'; /* Not set */
						}else{
							return '---'; /* Not set */
						}
					}
    			}
  			},
        	leaderRanks: {},
			leaderRank : function(str, role) {
				var _this = this;
				if(!angular.isDefined(role)){
	    			return _this.leaderRanks.length ? null : $http.get('role-types/leader/facets/rank/classes/').success(function(response) {
	      				_this.leaderRanks = response;
	    			});
    			}else{
					if(angular.isDefined(str) && _this.leaderRanks && _this.leaderRanks.length) {
						var selected = $filter('filter')(_this.leaderRanks, {uuid: str.uuid});
						return selected.length ? selected[0].name : '---'; /* Not set */
					} else {
						if(angular.isDefined(str)){
							return str.name || '---'; /* Not set */
						}else{
							return '---'; /* Not set */
						}
					}
    			}
  			},
			leaderRelatedEngagements: {},
			leaderRelatedEngagement : function(str, role) {
				var _this = this;
				if(!angular.isDefined(role)){
					return _this.leaderRelatedEngagements.length ? null : $http.get('e/'+$scope.empUUID+'/role-types/engagement/').success(function(response) {
						_this.leaderRelatedEngagements = response;
					});
				}else{
					if(angular.isDefined(str) && _this.leaderRelatedEngagements && _this.leaderRelatedEngagements.length) {
						var selected = $filter('filter')(_this.leaderRelatedEngagements, {uuid: str.uuid});
						return selected.length ? selected[0].name : '---'; /* Not set */
					} else {
						if(angular.isDefined(str)){
							return str.name || '---'; /* Not set */
						}else{
							return '---'; /* Not set */
						}
					}
				}
			},
			leaderAddress : [],
			leaderAddressEnable : false,
			loadLeaderAddress : function(uuid){
				var _this = this;
				_this.leaderAddress = [];
				$http.get('o/'+$scope.organizations[0].uuid+'/org-unit/'+uuid+'/role-types/location?effective-date='+validFrom).then(function(response) {
					var location = response.data;
					angular.forEach(location, function(value, index){
						$http.get('lokation/'+value.uuid).then(function(res) {
							_this.leaderAddress.push(res.data);
							_this.leaderAddressEnable = true;
						});
					})
				});
			},
			leaderAddressList : [],
			leaderAddressFunc : function(adress, uuid, validFrom) {
				var _this = this;
				_this.leaderAddressList = [];
				var prom = []
				validFrom = $filter('date')(validFrom, 'dd-MM-yyyy');
				$http.get('o/'+$scope.organizations[0].uuid+'/org-unit/'+uuid+'/role-types/location?effective-date='+validFrom).then(function(response) {
					var location = response.data;
					var prom = [];
					angular.forEach(location, function(value, index){
						prom.push($http.get('lokation/'+value.uuid).then(function(res) {
							_this.leaderAddressList.push(res.data);
						}));
					})
				});

				$q.all(prom).then(function () {
					return _this.leaderAddressFunc.length ? [] : _this.leaderAddressFunc;
				});
			},
			showLeaderAddress : function(row) {
				var _this = this;
				//_this.leaderAddressList = [];
				if(angular.isDefined(row['associated-adress']) && _this.leaderAddressList.length) {
					var selected = $filter('filter')(_this.leaderAddressList, {uuid: row['associated-adress'].uuid});
					return selected.length ? selected[0].name : '---'; /* Not set */
				} else {
					if(angular.isDefined(row['associated-adress'])){
						return row['associated-adress'].name || '---'; /* Not set */
					}else{
						return '---'; /* Not set */
					}
				}
			},
  			leaderFuncs: {},
			leaderFunc : function(str, role) {
				var _this = this;
				if(!angular.isDefined(role)){
	    			return _this.leaderFuncs.length ? null : $http.get('role-types/leader/facets/function/classes/').success(function(response) {
	      				_this.leaderFuncs = response;
	    			});
    			}else{
					if(angular.isDefined(str) && _this.leaderFuncs && _this.leaderFuncs.length) {
						var selected = $filter('filter')(_this.leaderFuncs, {uuid: str.uuid});
						return selected.length ? selected[0].name : '---'; /* Not set */
					} else {
						if(angular.isDefined(str)){
							return str.name || '---'; /* Not set */
						}else{
							return '---'; /* Not set */
						}
					}
    			}
  			},
        	leaderResponsibilities: {},
			leaderResponsibility : function(str, role) {
				var _this = this;
				if(!angular.isDefined(role)){
	    			return _this.leaderResponsibilities.length ? null : $http.get('role-types/leader/facets/responsibility/classes/').success(function(response) {
	      				_this.leaderResponsibilities = response;
	    			});
    			}else{
					if(angular.isDefined(str) && _this.leaderResponsibilities && _this.leaderResponsibilities.length) {
						var selected = $filter('filter')(_this.leaderResponsibilities, {uuid: str.uuid});
						return selected.length ? selected[0].name : '---'; /* Not set */
					} else {
						if(angular.isDefined(str)){
							return str.name || '---'; /* Not set */
						}else{
							return '---'; /* Not set */
						}
					}
    			}
  			},
			taskNames: {},
			taskName : function(str, role) {
				var _this = this;
				if(!angular.isDefined(role)){
	    			return _this.taskNames.length ? null : $http.get('role-types/job-function/facets/task/classes/').success(function(response) {
	      				_this.taskNames = response;
	    			});
    			}else{
					if(angular.isDefined(str) && _this.taskNames && _this.taskNames.length) {
						var selected = $filter('filter')(_this.taskNames, {uuid: str.uuid});
						return selected.length ? selected[0].name : '---'; /* Not set */
					} else {
						if(angular.isDefined(str)){
							return str.name || '---'; /* Not set */
						}else{
							return '---'; /* Not set */
						}
					}
    			}
  			},
			contactProperties: {},
			contactProperty : function(str, role) {
				var _this = this;
				if(!angular.isDefined(role)){
	    			return _this.contactProperties.length ? null : $http.get('role-types/contact/facets/properties/classes/').success(function(response) {
	      				_this.contactProperties = response;
	    			});
    			}else{
					if(angular.isDefined(str) && _this.contactProperties && _this.contactProperties.length) {
						var selected = $filter('filter')(_this.contactProperties, {uuid: str.uuid});
						return selected.length ? selected[0].name : '---'; /* Not set */
					} else {
						if(angular.isDefined(str)){
							return str.name || '---'; /* Not set */
						}else{
							return '---'; /* Not set */
						}
					}
    			}
  			},
  			contactTypes: {},
			contactType : function(str, role) {
				var _this = this;
				if(!angular.isDefined(role)){
	    			return _this.contactTypes.length ? null : $http.get('role-types/contact/facets/type/classes/').success(function(response) {
	      				_this.contactTypes = response;
	    			});
    			}else{
					if(angular.isDefined(str) && _this.contactTypes && _this.contactTypes.length) {
						var selected = $filter('filter')(_this.contactTypes, {uuid: str.uuid});
						return selected.length ? selected[0].name : '---'; /* Not set */
					} else {
						if(angular.isDefined(str)){
							return str.name || '---'; /* Not set */
						}else{
							return '---'; /* Not set */
						}
					}
    			}
  			},
  			relatedRoles: [],
			relatedRole : function(str, role) {
				var _this = this;
				if(!angular.isDefined(role)){
					if(_this.relatedRoles.length){
						return null;
					}else{
						var prom = [];
						var promLeader = [];
						var promEngagement = [];
						var roles = [];
						
						/*$http.get('e/' + $scope.empUUID + '/role-types/leader/').success(function(response) {
							promLeader.push(angular.forEach(response, function(value, index){
								roles.push(value);
							}));
						});*/

						$http.get('e/' + $scope.empUUID + '/role-types/engagement/').success(function(response) {
							promEngagement.push(angular.forEach(response, function(value, index){
								roles.push(value);
							}));
						});

						$q.all([promLeader, promEngagement]).then(function (result) {
							return _this.relatedRoles = roles;
						});
					}
    			}else{
    				if(angular.isDefined(str) && _this.relatedRoles && _this.relatedRoles.length) {
						var selected = $filter('filter')(_this.relatedRoles, {uuid: str.uuid});
						return selected.length ? selected[0].name : '---'; /* Not set */
					} else {
						if(angular.isDefined(str)){
							return str.name || '---'; /* Not set */
						}else{
							return '---'; /* Not set */
						}
					}
    			}
  			},
  			absenceTypes: {},
			absenceType : function(str, role) {
				var _this = this;
				if(!angular.isDefined(role)){
	    			return _this.absenceTypes.length ? null : $http.get('role-types/absence/facets/type/classes/').success(function(response) {
	      				_this.absenceTypes = response;
	    			});
    			}else{
					if(angular.isDefined(str) && _this.absenceTypes && _this.absenceTypes.length) {
						var selected = $filter('filter')(_this.absenceTypes, {uuid: str.uuid});
						return selected.length ? selected[0].name : '---'; /* Not set */
					} else {
						if(angular.isDefined(str)){
							return str.name || '---'; /* Not set */
						}else{
							return '---'; /* Not set */
						}
					}
    			}
  			},
  			itSystems: {},
			itSystem : function(str, role) {
				var _this = this;
				if(!angular.isDefined(role)){
	    			return _this.itSystems.length ? null : $http.get('it/').success(function(response) {
	      				_this.itSystems = response;
	    			});
    			}else{
					if(angular.isDefined(str) && _this.itSystems && _this.itSystems.length) {
						var selected = $filter('filter')(_this.itSystems, {uuid: str.uuid});
						return selected.length ? selected[0].name : '---'; /* Not set */
					} else {
						if(angular.isDefined(str)){
							return str.name || '---'; /* Not set */
						}else{
							return '---'; /* Not set */
						}
					}
    			}
  			},
  			// Association /////////////////////////////////////////////////////////////////////////////////////////////////////
			assocRoles: {},
			assocRole : function(str, role) {
				var _this = this;
				if(!angular.isDefined(role)){
					return _this.assocRoles.length ? null : $http.get('role-types/association/facets/associated-role/classes/').success(function(response) {
						response = _.without(response, _.findWhere(response, {name: 'Leder'}));
						_this.assocRoles = response;
					});
				}else{
					if(angular.isDefined(str) && _this.assocRoles && _this.assocRoles.length) {
						var selected = $filter('filter')(_this.assocRoles, {uuid: str.uuid});
						return selected.length ? selected[0].name : '---'; /* Not set */
					} else {
						if(angular.isDefined(str)){
							return str.name || '---'; /* Not set */
						}else{
							return '---'; /* Not set */
						}
					}
				}
			},
			associationTitles: {},
			associationTitle : function(str, role) {
				var _this = this;
				if(!angular.isDefined(role)){
					return _this.associationTitles.length ? null : $http.get('role-types/association/facets/job-title/classes/').success(function(response) {
						_this.associationTitles = response;
					});
				}else{
					if(angular.isDefined(str) && _this.associationTitles && _this.associationTitles.length) {
						var selected = $filter('filter')(_this.associationTitles, {uuid: str.uuid});
						return selected.length ? selected[0].name : '---'; /* Not set */
					} else {
						if(angular.isDefined(str)){
							return str.name || '---'; /* Not set */
						}else{
							return '---'; /* Not set */
						}
					}
				}
			},
			relatedEngagements: {},
			relatedEngagement : function(str, role) {
				var _this = this;
				if(!angular.isDefined(role)){
					return _this.relatedEngagements.length ? null : $http.get('e/'+$scope.empUUID+'/role-types/engagement/').success(function(response) {
						_this.relatedEngagements = response;
					});
				}else{
					if(angular.isDefined(str) && _this.relatedEngagements && _this.relatedEngagements.length) {
						var selected = $filter('filter')(_this.relatedEngagements, {uuid: str.uuid});
						return selected.length ? selected[0].name : '---'; /* Not set */
					} else {
						if(angular.isDefined(str)){
							return str.name || '---'; /* Not set */
						}else{
							return '---'; /* Not set */
						}
					}
				}
			},
			assocAddress : [],
			addressEnable : false,
			loadAddress : function(uuid, date, index){
				var _this = this;
				_this.assocAddress[index] = {};
				var date = $filter('date')(date, 'dd-MM-yyyy');
				$http.get('o/'+$scope.$parent.organizations[0].uuid+'/org-unit/'+uuid+'/role-types/location?effective-date='+date).success(function(response) {
					_this.assocAddress[index] = response;
					_this.addressEnable = true;
				});
			},
			showAssocAddress : function(address, key, index) {
				var _this = this;
				if(angular.isDefined(address) && angular.isDefined(_this.assocAddress[index])) {
					var selected = $filter('filter')(_this.assocAddress[index], {uuid: address.uuid});
					return selected.length ? selected[0].name : '---';
				} else {
					if(angular.isDefined(address)){
						return address.name || '---';
					}else{
						return '---';
					}
				}
			},
  			updRowBeforeSave: function(row, field, _this){
  				if(field == "valid-from" || field == "valid-to"){
  					row[field+'-updated'] = _this;
  					if(field == "valid-from" && (!angular.isDefined(_this) || _this == "" || !sysService.dateFormat.validateInput(_this))){
  						return $rootScope.i18n["enter_valid-from_date"];
  					}

  					if(field == "valid-to" && !sysService.dateFormat.validateInput(_this) && _this != "" && _this !== null){
  						return $rootScope.i18n["enter_valid-to_date"];
  					}

  					var validFrom = row['valid-from'];
  					if(angular.isDefined(row['valid-from-updated']) && row['valid-from-updated'] != ''){
						validFrom = row['valid-from-updated'];
					}

					var validTo = row['valid-to'];
  					if(angular.isDefined(row['valid-to-updated']) && row['valid-to-updated'] != ''){
						validTo = row['valid-to-updated'];
					}

					validFrom = $filter('date')(validFrom, "dd-MM-yyyy");
					validTo = (validTo == "" || validTo === null)?"":$filter('date')(validTo, "dd-MM-yyyy");

					// Validation
					validFrom=validFrom.split("-");
					validFrom=validFrom[1]+"/"+validFrom[0]+"/"+validFrom[2];

					if(validTo != ""){
						validTo=validTo.split("-");
						validTo=validTo[1]+"/"+validTo[0]+"/"+validTo[2];					
					}

					if(validTo != ""){
						if (new Date(validTo).getTime() < new Date(validFrom).getTime()) {
						    return $rootScope.i18n["enter_valid_date_range"];
						}
					}
				}else if(field == "phone-type"){
					var _editEmpFuncObj = this;
	    			var selected = $filter('filter')(_editEmpFuncObj.contactTypes, {uuid: _this});
					row['type-updated'] = selected.length ? selected[0].name : '';
				}else if(field == "contact-info"){
					var errorMessage = '';
					var rowType = row['phone-type'].name;

					if(angular.isDefined(row['type-updated']) && row['type-updated'] != ''){
						rowType = row['type-updated'];
					}
					if(rowType == "Telefonnummer" && _this.length != 8){
						errorMessage = $rootScope.i18n["organization_error_validation_min-length_contact-info-Telefonnummer"];
						return errorMessage;
					}
				}else{
  					if(angular.isDefined(row[field])){ return; }else{ return row[field] = {}; }
  				}
  			},
			updRow : function(type, index, period, data){
				var row = $scope.$parent.tables[type]['tr'][period][index];
				$scope.$parent.flag.dataUnsaved = true;
				if(angular.isDefined(row.uuid)){
					$scope.$parent.engagements[type].changed = true;
					row.changed = true;
	  				$scope.$parent.flag.dataUpdated = true;
  				}
  			},
			saveRows : function(){
				var _this = this;
  				// Reset validation
				angular.forEach(this.validationError, function(value, key){
					_this.validationError[value] = "";
				});
  				if($scope.$parent.flag.dataUpdated){
					$scope.$parent.flag.orgEditSuccess = false;

					var editPromise = [];
					var createPromise = [];
					angular.forEach($scope.$parent.engagements, function(role, key){
						var postObj = $scope.$parent.tables[key]['tr'];
						role.errorCreate = false; role.errorUpdate = false;
						angular.forEach(postObj, function(value, k){
							angular.forEach(value, function(data, dataKey){
								if(!angular.isDefined(data.uuid) && angular.isDefined(role.added) && role.added){ // CREATE
									data["valid-from"] = $filter('date')(data["valid-from"], 'dd-MM-yyyy');
									data["valid-to"] = $filter('date')(data["valid-to"], 'dd-MM-yyyy');

									var postData = JSON.stringify(data);
						   			createPromise.push(empFactory.empCreate(key, $scope.$parent.empUUID, postData).then(function(response) { // Post Success
										var res = empFactory.empCreateRes();
										if(res.response){ // Post Success
						   					if(key == 'association'){ $scope.editEmployeeFunc.assocAddressEnable = false; }
										}else{ // Post Error
											role.errorCreate = true;
											role.errorCreateMessage = (res.data["errors"])?res.data["errors"]:{};
										}
									},function(error){
									}));
								}else if(angular.isDefined(data.uuid) && angular.isDefined(data.changed) && data.changed){ // UPDATE
									data["valid-from"] = $filter('date')(data["valid-from"], 'dd-MM-yyyy');
									data["valid-to"] = $filter('date')(data["valid-to"], 'dd-MM-yyyy');

									var postData = JSON.stringify(data);
									editPromise.push(empFactory.empUpdateRole(key, $scope.$parent.empUUID, data["uuid"], JSON.stringify(data)).then(function(response) { // Post Success
										var data = response.data;
										if(response.status == 200){ // Post Success
										}else{ // Post Error
											role.errorUpdate = true;
											role.errorUpdateMessage = (data["errors"])?data["errors"]:{};
										}
									},function(error){
									}));
								}
							});
						});
					});

					$q.all(createPromise).then(function (result) {
						$q.all(editPromise).then(function (result) {
							var deferred = $q.defer();
							var prom = deferred.promise;
							var closeModal = true;
							prom.then(function () {
								angular.forEach($scope.$parent.engagements, function(role, key){
									if((angular.isDefined(role.changed) && role.changed) || (angular.isDefined(role.added) && role.added)){
										if(angular.isDefined(role.errorUpdate) && role.errorUpdate){
											closeModal = false;
											$scope.$parent.flag.dataUnsaved = true;
										}else if(angular.isDefined(role.errorCreate) && role.errorCreate){
											closeModal = false;
											$scope.$parent.flag.dataUnsaved = true;
										}else{
											$scope.$parent.flag.dataUnsaved = false;
											role.errorCreate = false;
											role.errorUpdate = false;
											role.changed = false;
											role.added = false;
											if(sysService.state.data.page.key == "employee" && sysService.state.data.page.subKey == "detail"){
												$scope.$parent.loadEngagements($scope.$parent.empUUID, key);
											}
										}
									}
								});
							}).then(function () {
								if(closeModal){
									sysService.recordEvent.set('success', sysService.i18n('employee_updated_successfully'));
									$scope.$parent.flag.dataUpdated = false;
									$scope.$parent.empEdit('close');
								}
							});
							$timeout(function() {
								deferred.resolve();
							}, 2000);
						});
					});


  				}
  			}
		}

		$scope.$on('orgUnitSelected', function(event, data) { 
	  		$scope.createEmployeeFunc.addressEnable = false;
			$scope.createEmployeeFunc.loadAddress(node.uuid, $scope.empObj.valid_from);
	  	});
		$scope.$watch('empObj.valid_from', function(newVal) { 
			if(angular.isDefined(newVal)){
	  			$scope.createEmployeeFunc.addressEnable = false;
				$scope.createEmployeeFunc.loadAddress(empObj.org_unit.uuid, newVal);
			}
	  	});

		hotkeys.add({
			combo: sysService.shortcuts.popupClose.key,
			description: sysService.shortcuts.popupClose.title,
			callback: function() {
				if($scope.$parent.empViewOpen || $scope.$parent.empEditOpen){
					if(!$scope.$parent.editEmployee){ //View popup close 
						$scope.$parent.empView('close');
					}else{ //Edit popup close
						$scope.$parent.empEdit('close');
					}
				}
			}
		});

		hotkeys.add({
			combo: sysService.shortcuts.popupSubmit.key,
			description: sysService.shortcuts.popupSubmit.title,
			callback: function() {
				if($scope.$parent.empEditOpen && $scope.$parent.flag.dataUpdated){
					$scope.editEmployeeFunc.saveRows();
				}
			}
		});
	}]);
	
