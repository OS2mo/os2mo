'use strict';
/* Employee controllers */

angular.module('moApp.controllers').
	controller('employeeCreateEngagement',["$scope", 'empFactory', "$filter", "$rootScope", "sysService", "$http", "$q",function($scope, empFactory, $filter, $rootScope, sysService, $http, $q) {
		var errorMessage = {};
		$scope.cleanUp = function(){
			$scope.createEngagement = false;
			$scope.dataAdding = false;
			$scope.validationError = false;
			$scope.empObj = {}; 
			$scope.validationErrorMsg = {};
			errorMessage = {};
		};
		$scope.cleanUp();
		$scope.cancelForm = function(){
			$scope.cleanUp();
		};

		$scope.createEmployeeFunc = {
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
  			},
			leaderTitles: {},
			leaderTitle : function(str, role) {
				var _this = this;
				return _this.leaderTitles.length ? null : $http.get('role-types/leader/facets/title/classes/').success(function(response) {
      				_this.leaderTitles = response;
    			});
  			},
        	leaderRanks: {},
			leaderRank : function(str, role) {
				var _this = this;
				return _this.leaderRanks.length ? null : $http.get('role-types/leader/facets/rank/classes/').success(function(response) {
      				_this.leaderRanks = response;
    			});
  			},
  			leaderFuncs: {},
			leaderFunc : function(str, role) {
				var _this = this;
    			return _this.leaderFuncs.length ? null : $http.get('role-types/leader/facets/function/classes/').success(function(response) {
      				_this.leaderFuncs = response;
    			});
  			},
        	leaderResponsibilities: {},
			leaderResponsibility : function(str, role) {
				var _this = this;
				return _this.leaderResponsibilities.length ? null : $http.get('role-types/leader/facets/responsibility/classes/').success(function(response) {
      				_this.leaderResponsibilities = response;
    			});
  			},
			taskNames: {},
			taskName : function(str, role) {
				var _this = this;
				return _this.taskNames.length ? null : $http.get('role-types/job-function/facets/task/classes/').success(function(response) {
      				_this.taskNames = response;
    			});
  			},
			contactProperties: {},
			contactProperty : function(str, role) {
				var _this = this;
    			return _this.contactProperties.length ? null : $http.get('role-types/contact/facets/properties/classes/').success(function(response) {
      				_this.contactProperties = response;
    			});
  			},
  			contactTypes: {},
			contactType : function(str, role) {
				var _this = this;
    			return _this.contactTypes.length ? null : $http.get('role-types/contact/facets/type/classes/').success(function(response) {
      				_this.contactTypes = response;
    			});
  			},
  			relatedRoles: [],
			relatedRole : function(str, role) {
				var _this = this;
				if(_this.relatedRoles.length){
					return null;
				}else{
					var prom = [];
					var promLeader = [];
					var promEngagement = [];
					var roles = [];

					$http.get('e/' + $scope.empUUID + '/role-types/engagement/').success(function(response) {
						promEngagement.push(angular.forEach(response, function(value, index){
							roles.push(value);
						}));
					});

					$q.all([promLeader, promEngagement]).then(function (result) {
						return _this.relatedRoles = roles;
					});
				}
  			},
  			absenceTypes: {},
			absenceType : function(str, role) {
				var _this = this;
    			return _this.absenceTypes.length ? null : $http.get('role-types/absence/facets/type/classes/').success(function(response) {
      				_this.absenceTypes = response;
    			});
  			},
  			itSystems: {},
			itSystem : function(str, role) {
				var _this = this;
    			return _this.itSystems.length ? null : $http.get('it-system/').success(function(response) {
      				_this.itSystems = response;
    			});
  			},
  			relatedEngagements: {},
			relatedEngagement : function(str, role) {
				var _this = this;
				return _this.relatedEngagements.length ? null : $http.get('e/'+$scope.empUUID+'/role-types/engagement/').success(function(response) {
					_this.relatedEngagements = response;
				});
			},
			assocRoles: {},
			assocRole : function(str, role) {
				var _this = this;
				return _this.assocRoles.length ? null : $http.get('role-types/association/facets/associated-role/classes/').success(function(response) {
					response = _.without(response, _.findWhere(response, {name: 'Leder'}));
					_this.assocRoles = response;
				});
			},
			associationTitles: {},
			associationTitle : function(str, role) {
				var _this = this;
				return _this.associationTitles.length ? null : $http.get('role-types/association/facets/job-title/classes/').success(function(response) {
					_this.associationTitles = response;
				});
			
			},
			assocAddress : {},
			addressEnable : false,
			loadAddress : function(uuid, date){
				var _this = this;
				_this.assocAddress = {};
				var date = $filter('date')($scope.empObj['valid_from'], 'dd-MM-yyyy');
				$http.get('o/'+$scope.$parent.organizations[0].uuid+'/org-unit/'+uuid+'/role-types/location?effective-date='+date).success(function(response) {
					_this.assocAddress = response;
					_this.addressEnable = true;
				});
			}
		}

		$scope.$on('empObj.valid_from', function(event, data) { 
	  		$scope.empObj.org_unit = null;	
	  		$scope.createEmployeeFunc.assocAddress = {};	
	  		$scope.createEmployeeFunc.addressEnable = false;
	  		$scope.empObj.associated_adress = {};
	  	});

	  	$scope.$parent.$watch("globalStartDate", function(newVal){
	  		if(angular.isDefined(newVal)){
	  			$scope.empObj.valid_from = newVal;
	  		}
	  	})

	  	$scope.$parent.$watch("globalEndDate", function(newVal){
	  		if(angular.isDefined(newVal)){
	  			$scope.empObj.valid_to = newVal;
	  		}
	  	})

		$scope.engagementCreate = function(section){
			$scope.createEmployeeFunc.jobTitle();			
			$scope.createEmployeeFunc.empType();

			$scope.createEmployeeFunc.leaderTitle();			
			$scope.createEmployeeFunc.leaderRank();			
			$scope.createEmployeeFunc.leaderFunc();			
			$scope.createEmployeeFunc.leaderResponsibility();			

			$scope.createEmployeeFunc.taskName();			
			$scope.createEmployeeFunc.contactProperty();			
			$scope.createEmployeeFunc.contactType();			

			$scope.createEmployeeFunc.relatedRole();			
			$scope.createEmployeeFunc.absenceType();			
			$scope.createEmployeeFunc.itSystem();

			$scope.createEmployeeFunc.relatedEngagement();						
			$scope.createEmployeeFunc.assocRole();						
			$scope.createEmployeeFunc.associationTitle();						
		}

		$scope.engagementEdit = function(section){
			$scope.editEmployeeFunc.jobTitle();			
			$scope.editEmployeeFunc.empType();

			$scope.editEmployeeFunc.leaderTitle();			
			$scope.editEmployeeFunc.leaderRank();			
			$scope.editEmployeeFunc.leaderFunc();			
			$scope.editEmployeeFunc.leaderResponsibility();			

			$scope.editEmployeeFunc.taskName();			
			$scope.editEmployeeFunc.contactProperty();			
			$scope.editEmployeeFunc.contactType();			

			$scope.editEmployeeFunc.relatedRole();			
			$scope.editEmployeeFunc.absenceType();			
			$scope.editEmployeeFunc.itSystem();

			$scope.editEmployeeFunc.relatedEngagement();						
			$scope.editEmployeeFunc.assocRole();						
			$scope.editEmployeeFunc.associationTitle();
		}

		$scope.saveEmployee = function(section, empUUID, state, obj){
			$scope.validationErrorMsg = {"error": false, "section": section	, "response": ""};
			$scope.$parent.flag.empCreateSuccess = false;
			errorMessage = {};
			// validation
			if($scope.empCreateForm.$error.required.length > 0){ // Validation fail
				$scope.validationError = true;
				var errors = $scope.empCreateForm.$error.required
				angular.forEach(errors, function(value, key) {
					errorMessage[value.$name] = {"message": $rootScope.i18n[section+"_error_validation_required_"+value.$name]};
				}, errorMessage);
				$scope.validationErrorMsg = {"error": true, "section": section, "response": errorMessage};
			}else if(section == "contact" && angular.isDefined(obj.empObj.phone_type) && obj.empObj.phone_type.name == "Telefonnummer" && angular.isDefined(obj.empObj.contact_info) && obj.empObj.contact_info.length != 8){
				$scope.validationError = true;
				errorMessage['contact'] = {"message": $rootScope.i18n["organization_error_validation_min-length_contact-info-Telefonnummer"]};
				$scope.validationErrorMsg = {"error": true, "section": section, "response": errorMessage};
			}else{ // Validation pass
				// Post data
				$scope.validationError = false;
				var postData = {};
				$scope.empObj.valid_from = ($scope.empObj.valid_from == "")?"infinity":$filter('date')($scope.empObj.valid_from, "dd-MM-yyyy");
				$scope.empObj.valid_to = ($scope.empObj.valid_to == "")?"infinity":$filter('date')($scope.empObj.valid_to, "dd-MM-yyyy");

				angular.forEach($scope.empObj, function(value, key) {
					key = key.replace(/_/g, '-');
					if(value != "" && value && typeof(value) !== "undefined"){
						postData[key] = value;
					}else{
						//$scope.validationError = true;
					}
				}, postData);
				postData["person"]=empUUID;
				postData["role-type"]=section;
				postData["user-key"]="NULL";

				var validityState;
				var startDate = $scope.empObj.valid_from;
				startDate=startDate.split("-");
				startDate=startDate[1]+"/"+startDate[0]+"/"+startDate[2];

				var endDate = $scope.empObj.valid_to;
				if(endDate === null || endDate == "" || endDate == "infinity" || !angular.isDefined(endDate)){
					endDate = '';
				}else{
					endDate=endDate.split("-");
					endDate=endDate[1]+"/"+endDate[0]+"/"+endDate[2];					
				}

				if(endDate != ""){
					if (new Date(endDate).getTime() < new Date().getTime()) {
					    validityState = 'past';
					}else if (new Date(endDate).getTime() >= new Date().getTime()) {
					    validityState = 'present';
					}else if (new Date(startDate).getTime() > new Date().getTime()) {
						validityState = 'future';
					}
				}else{
					if (new Date(startDate).getTime() <= new Date().getTime()) {
					    validityState = 'present';
					}else if (new Date(startDate).getTime() > new Date().getTime()) {
						validityState = 'future';
					}
				}
				if(angular.isDefined(state) && state.name == "new"){ // New employee code
					if(endDate != ""){
						if (new Date(endDate).getTime() < new Date(startDate).getTime()) {
							$scope.validationError = true;
							errorMessage[section] = {"message": $rootScope.i18n["enter_valid_date_range"]};
							$scope.validationErrorMsg = {"error": true, "section": section, "response": errorMessage};
						}
					}
					if(!$scope.validationError){
						$scope.$parent.engagements[section].data.push(postData);
						$scope.createEngagement = false;
						$scope.empObj = null;
					}
				}else{
					$scope.engagementEdit();
					
					if(endDate != ""){
						if (new Date(endDate).getTime() < new Date(startDate).getTime()) {
							$scope.validationError = true;
							errorMessage[section] = {"message": $rootScope.i18n["enter_valid_date_range"]};
							$scope.validationErrorMsg = {"error": true, "section": section, "response": errorMessage};
						}
					}
					if(!$scope.validationError){
						$scope.$parent.tables[section]['tr'][validityState].push(postData);
						$scope.engagements[section][validityState] = true;
						$scope.engagements[section]['display'] = true;
						$scope.engagements[section]['defaultTab'] = 'present';
						$scope.engagements[section]['visible'] = 'present';
						$scope.engagements[section][validityState] = true;
						$scope.$parent.flag.dataUpdated = true;
						$scope.$parent.flag.dataUnsaved = true;
						$scope.engagements[section]['added'] = true;
						$scope.createEngagement = false;
						$scope.empObj = null;
					}
				}
			}
		}
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
        		var date = (angular.isDefined($scope.empObj.valid_from) && $scope.empObj.valid_from != "")?$filter('date')($scope.empObj.valid_from, "dd-MM-yyyy"):"";
    	    	return $http.get('o/'+o[0].uuid+'/full-hierarchy', 
    	    		{ params: { query: val, 'effective-date': date}}
    	    	).then(function(response){
    	    		var resData = response.data;   
    	    		$scope.$broadcast("typeAheadData", [resData.hierarchy]);
    	    		$scope.enHeadUnits =  false;
    	    	});
        	}
        };
	    $scope.selectNode = function(node,calledFrom){    		
			$scope.valueEnhead =  node.name;
			$scope.selectedEnhead = node;			
			console.log("Load address");
			$scope.createEmployeeFunc.addressEnable = false;
			$scope.createEmployeeFunc.loadAddress(node.uuid);
			$scope.empObj.org_unit = node;	
        };

        $scope.$on("hideTypeAheadTree", function(event){
    		$scope.isEnhead = false; 
    	});

    	$scope.dateSelect = function(dateField){
    		var date = $scope.empObj[dateField];
    		if(sysService.dateFormat.validateInput(date)){
    			date = $filter('date')(date, 'dd-MM-yyyy');
    			$scope[dateField] = date;
    			if(dateField == "valid_from"){
    				$scope.empObj.org_unit = {};	
    				$scope.valueEnhead = '';
    				$scope.isEnhead = false;
	    			$scope.enHeadUnits = false;
					$scope.createEmployeeFunc.assocAddressEnable = false;
    			}
    		}
    	};

}]);

