'use strict';
/* Employee controllers */ 

angular.module('moApp.controllers')
	.controller('employeeNew',["$scope", "$filter", "$rootScope", '$http', "empFactory", "sysService", 'hotkeys', '$q', function($scope, $filter, $rootScope, $http, empFactory, sysService, hotkeys, $q) {		
		$scope.workFlowNewFlag = {
			invalid : false,
			found : false,
			notFound : false,
			notFoundMessage : {},
			fail : false,
			success : false,
			details : false,
			rolesNotFound: false,
	  		empInfoLoaded: false,
	  		dataUpdated: false,
	  		dataAdded: false,
	  		empEngagementsFound: false,
	  		empEngagementsLoaded: false
		}
		var active = false;
		var errorMessage = [];
		$scope.globalStartDate;
		$scope.globalEndDate;

		$scope.validationErrorMsg = {"error": false, "section":'', "response": ''};
		$scope.validity = ['present', 'past', 'future'];
		$scope.engagements = {
			"engagement":{ "key": "engagement", "visible":false, data: [], error: []},
			"association":{"key": "association", "visible":false, data: [], error: []},
			"it":{"key": "it", "visible":false, data: [], error: []},
			"contact":{"key": "contact", "visible":false, data: [], error: []},
			"leader":{"key": "leader", "visible":false, data: [], error: []}
        }

		$scope.empCPRSearch = function(){
			$scope.workFlowNewFlag = {
				invalid : false,
				found : false,
				notFound : false,
				endFail : false,
				endSuccess : false,
				details : false,
				rolesNotFound: false,
		  		empInfoLoaded: false,
		  		empEngagementsFound: false,
		  		empEngagementsLoaded: false
			}
	        empFactory.empHeaders().then(function(response) {
				$scope.tables = response;
			});
			if(typeof (this.empCPR) !== "undefined" && this.empCPR != ""){					
				empFactory.empInfosByCPR(this.empCPR).then(function(response){
						var empUUID = response["uuid"]; 
						$scope.employee = response;
						$scope.empCPR = response["user-key"]; 
						$scope.empUUID = response["uuid"]; 
						$scope.visibleEngagementsCount = 0;
						$scope.workFlowNewFlag.found = true;
						$scope.workFlowNewFlag.empInfoLoaded = true;
						active = false;
						angular.forEach($scope.engagements, function(role, key){
							$scope.loadEngagements(empUUID, key);
						});
					}, function(error){
						$scope.workFlowNewFlag.notFound = true;
						$scope.workFlowNewFlag.notFoundMessage = error.data['errors'];
				});
			}else{
				$scope.workFlowNewFlag.invalid = true;
			}
		}

		$scope.cleanUpEmpData = function(){
			angular.forEach($scope.tables, function(row, key){
				angular.forEach($scope.engagements, function(role, key){
					row.tr[role] = [];
				});
			});
			angular.forEach($scope.engagements, function(role, key){
				role.visible = false;
				angular.forEach($scope.validity, function(validity, position){
					role.data = [];
				});
			})
		};

		var activeEngagement = false;
		var existingEngagement = false;
		$scope.loadEngagements = function(cpr, engagement){
			var prom = [];
			var table = $scope.tables[engagement];
			var defaultTab = '';
			var visible = false;
			
			$scope.engagements[engagement]['visible'] = visible;
			angular.forEach($scope.validity, function(validity, position){
				table.tr[validity] = [];
				$scope.engagements[engagement][validity] = false; 
				prom.push(empFactory.empRoles(cpr, engagement, '', validity).then(function(response){
					table.tr[validity] = [];
					table.tr[validity] = response;
					if(engagement == "engagement"){
						$scope.existingEngagement = true;
					}
					if(response.length > 0){
						// Set default tab
						if(!activeEngagement){ activeEngagement = true; $scope.engagements[engagement].active = true;}
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
							role.defaultTab = validity;
							defaultTabSet = true;
							$scope.workFlowNewFlag.empEngagementsFound = true;
						}
					});
					$scope.engagements[engagement]['visible'] = true;
					$scope.visibleEngagementsCount++;
				}
			});
		};
		$scope.transferDateFunc = function(val){
			if(val.transferDate == 1){
				$scope.globalStartDate = $scope['valid_from'];
				$scope.globalEndDate = $scope['valid_to'];
			}else{
				$scope.globalStartDate = null;
				$scope.globalEndDate = null;
			}
		}

		// Load Orgs and OrgUnits
		sysService.orgList.fetch().then(function(response){
			$scope.organizations = response;
			sysService.loadOrgData.getUnits().then(function(response) {
	            $scope.orgUnits = response;
	        }, function(error){ // No child units
	        });
		});

		$scope.createEmployeeEngagementFunc = {
        	jobTitles: {},
			jobTitle : function(str, role) {
				var _this = this;
				return _this.jobTitles.length ? null : $http.get('role-types/engagement/facets/job-title/classes/').success(function(response) {
      				_this.jobTitles = response;
    			});
			
  			},
  			empTypes: {},
			empType : function(str, role) {
				var _this = this;
    			return _this.empTypes.length ? null : $http.get('role-types/engagement/facets/type/classes/').success(function(response) {
      				_this.empTypes = response;
    			});
  			}
		}
		$scope.createEmployeeEngagementFunc.jobTitle();			
		$scope.createEmployeeEngagementFunc.empType();

		$scope.remove = function(key, row){
			var index = $scope.engagements[key].data.indexOf(row)
  			$scope.engagements[key].data.splice(index, 1);  
  			$scope.engagements[key]['error'] = [];
		}
		/*$scope.setDate = function(key, obj){
			$scope[key] = obj;
		}*/
		// Save data
		$scope.$parent.newEmpObj = {}; 
		$scope.saveEmployeeNewRoles = function(){
			$scope.validationErrorMsgEngagement = {"error": false, "section": 'engagement', "response": ""};
			var errorMessage = {};
				angular.forEach($scope.$parent.newEmpObj, function(value, key) {
					if(value != "" && value && typeof(value) !== "undefined"){
					}else{
						delete $scope.$parent.newEmpObj[key];
					}
				});
				if(angular.isDefined($scope.$parent.newEmpObj) && _.size($scope.$parent.newEmpObj) > 0){
					// Validations
					if($scope.empCreateForm.$error.required.length > 0){ // Validation fail
						var errors = $scope.empCreateForm.$error.required;
						angular.forEach(errors, function(value, key) {
							errorMessage[value.$name] = {"message": $rootScope.i18n["engagement_error_validation_required_"+value.$name]};
						}, errorMessage);
						$scope.validationErrorMsgEngagement = {"error": true, "section": 'engagement', "response": errorMessage};
					}else{
						var postData = {};
						$scope.$parent.newEmpObj.valid_from = ($scope.$parent.newEmpObj.valid_from == "")?"infinity":$filter('date')($scope.$parent.newEmpObj.valid_from, "dd-MM-yyyy");
						$scope.$parent.newEmpObj.valid_to = ($scope.$parent.newEmpObj.valid_to == "")?"infinity":$filter('date')($scope.$parent.newEmpObj.valid_to, "dd-MM-yyyy");

						angular.forEach($scope.$parent.newEmpObj, function(value, key) {
							key = key.replace(/_/g, '-');
							if(value != "" && value && typeof(value) !== "undefined"){
								postData[key] = value;
							}else{
								$scope.validationError = true;
							}
						}, postData);
					
						postData["person"]=$scope.empUUID;
						postData["role-type"]='engagement';
						postData["user-key"]="NULL";
						$scope.engagements['engagement'].data.push(postData);	
					}
				}else{
					errorMessage = {};
				}
				if(_.size(errorMessage) < 1){
					var url = "/mo/e/"+$scope.empUUID+"/actions/role";
					var prom = [];
					var promRes = [];
					var success = true;
					angular.forEach($scope.engagements, function(role, key){
						if(role.data.length > 0){
							role.error = [];
							role.success = false;
							promRes.push(empFactory.empCreateNew(url, role.data, function(state, data){
								if(state){
									role.data = [];
									role.success = true;
									$scope.workFlowNewFlag.dataUpdated=true;
								}else{ // Error
									$scope.engagements['engagement'].data = [];
									$scope.workFlowNewFlag.fail = true;
									role.error = (data["errors"])?data["errors"]:[];
									success = false;
								}
							}));
						}else{
							success = true;
							promRes.push(success);
						}
					});
					$q.all(promRes).then(function (result) {
						if(success){ // Success // Close Modal
							if($scope.workFlowNewFlag.dataUpdated){
								sysService.recordEvent.set('success', sysService.i18n('employee_roles_added_successfully_label'));
								if(sysService.state.data.page.key == "employee" && sysService.state.data.page.subKey == "detail"){
									angular.forEach($scope.engagements, function(role, key){
										$scope.$parent.loadEngagements($scope.empUUID, key);
									});
								}
							}
							$scope.$parent.empNewModal('close');
							errorMessage = {};
						}else{ // Error
						}
					});
				}
			//}
		};

		$scope.datePickers = {'from': false, 'to': false};
		$scope.openDatePicker = function($event, cal) {
			$event.preventDefault();
			$event.stopPropagation();
			angular.forEach($scope.datePickers, function(value, key){
				if(key != cal){ $scope.datePickers[key] = false; }
			});
			$scope.datePickers[cal] = ($scope.datePickers[cal])?false:true;
		};

		$scope.isEnhead = false;
	    $scope.enHeadUnits = false;

	    $scope.onClickEnhead = function(){
	      $scope.isEnhead = true;
	      $scope.selectedEnhead = null;
	    };

	    $scope.onChangeOccured = function(val, calledFrom){
	    	if(val.length>=3){  
	    		var o = sysService.orgList.get();
		    	return $http.get('o/'+o[0].uuid+'/full-hierarchy', 
		    		{ params: { query: val, 'effective-date': $scope.startDateSelected}}
		    	).then(function(response){
		    		var resData = response.data;   
		    		$scope.$broadcast("typeAheadData", [resData.hierarchy]);
		    		$scope.enHeadUnits = false;
		    	});
			}
	    };

        $scope.$on("hideTypeAheadTree", function(event){
    		$scope.isEnhead =  false; 
    	});

    	$scope.selectNode = function(node,calledFrom){
			$scope.enhead =  node.name;
			$scope.selectedEnhead = node;
			$scope.newEmpObj.org_unit = node;
        };

        $scope.dateSelect = function(dateField){
        	var date = $scope.newEmpObj[dateField];
        	if(sysService.dateFormat.validateInput(date)){
        		if(dateField == "valid_from" && $scope.transferDate == 1){ $scope.globalStartDate = date; }
        		if(dateField == "valid_to" && $scope.transferDate == 1){ $scope.globalEndDate = date; }
        		date = $filter('date')(date, 'dd-MM-yyyy');
        		$scope[dateField] = date;
        	}
        };

		hotkeys.add({
			combo: sysService.shortcuts.popupSubmit.key,
			description: sysService.shortcuts.popupSubmit.title,
			callback: function() {
				$scope.saveEmployeeNewRoles();
			}
		});

		hotkeys.add({
			combo: sysService.shortcuts.popupClose.key,
			description: sysService.shortcuts.popupClose.title,
			callback: function() {
				$scope.$parent.empNewModal('close');
			}
		});

	}]);