'use strict';
/* Employee controllers */ 

angular.module('moApp.controllers').
	controller('employeeMoveMany',["$scope", 'empFactory', "$filter", "$rootScope", '$http', '$modal', 'sysService', '$q', function($scope, empFactory, $filter, $rootScope, $http, $modal, sysService, $q) {
		$scope.workFlowMoveManyFlag = {
			invalid : false,
			found : false,
			notFound : false,
			fail : false,
			failMessage: {},
			success : false,
			moved : false,
			details : false,
			infoLoaded: false,
			orgUnitFromFound: false,
			orgUnitFromResultFound: false,
			orgUnitToFound: false,
			step2: false,
			employeesNotFound: false,
			rolesFound: false
		};
		var _this = this;
		_this.empUUID;
		$scope.empName;
		$scope.original_org_unit;
		$scope.empMoveDate;
		$scope.tables;
		$scope.org_unit;

		$scope.originalOrgUnitEngagementsFound = false;
		$scope.originalOrgUnitEngagements;
		$scope.transferOrgUnitEngagements = [];
		$scope.currentEmpCounter = 0;

		$scope.validity = ['present', 'future'];
		$scope.engagements = {
			"engagement":{ "key": "engagement", "visible":false, "data": { "present": [], "future": [] }, defaultTab: 'present'},
			"association":{ "key": "association", "visible":false, "data": { "present": [], "future": [] }, defaultTab: 'present'}
        };

		$scope.cleanUpEmpData = function(){
			angular.forEach($scope.engagements, function(role, key){
				role.visible = false;
				role.data = { "present": [], "future": [] };
			});
			angular.forEach($scope.tables, function(row, key){
				angular.forEach($scope.engagements, function(role, key){
					row.tr[role] = [];
				});
			});
		};


		$scope.$watch('original_org_unit', function(newVal){
        	if(angular.isDefined(newVal) && newVal != ""){
        		$scope.workFlowMoveManyFlag.orgUnitFromFound = true;
				$scope.loadEngagementsForSelectedOrgUnit();
        	}
        })

		$scope.loadEngagementsForSelectedOrgUnit = function(){
			$scope.workFlowMoveManyFlag.employeesNotFound = false;
			var url = '/mo/o/'+$scope.original_org_unit.org+'/org-unit/'+$scope.original_org_unit.uuid+'/role-types/engagement?effective-date='+$scope.empMoveDate;
			$http.get(url).then(function(response) {
				angular.forEach(response.data, function(row, index) {					
					row.selected = false;					
				});
				$scope.originalOrgUnitEngagements = response.data;				
				$scope.workFlowMoveManyFlag.orgUnitFromResultFound = true;
			}, function(error){
				$scope.workFlowMoveManyFlag.employeesNotFound = true;
			});
		};

		$scope.empMoveEngagements = function() {
			$scope.transferOrgUnitEngagements = [];
			angular.forEach($scope.originalOrgUnitEngagements, function(row, index) {
				if(row.selected) {
					$scope.transferOrgUnitEngagements.push(row);
				}
			})

		};

		$scope.empMoveManyNextStep = function() {
			$scope.workFlowMoveManyFlag.orgUnitFromResultFound = false;
			$scope.workFlowMoveManyFlag.step2 = true;
			$scope.workFlowMoveManyFlag.details = false;
			if($scope.transferOrgUnitEngagements.length>0){ $scope.loadNextEmployeeOrClose(); }
		};

		var activeEngagement = false;
		var loadEngagements = function(cpr, engagement){
			var prom = [];
			var table = $scope.tables[engagement];
			var defaultTab = '';
			var visible = false;
			var state = false;
			$scope.workFlowMoveManyFlag.moved = false;

			$scope.engagements[engagement]['visible'] = visible;
			angular.forEach($scope.validity, function(validity, position){
				table.tr[validity] = [];
				$scope.engagements[engagement][validity] = false; 
				prom.push(empFactory.empRoles(cpr, engagement, $scope.empMoveDate, validity).then(function(response){
					table.tr[validity] = [];
					table.tr[validity] = response;
					if(response.length > 0){
						if(!activeEngagement){ activeEngagement = true; $scope.engagements[engagement].active = true;}
						$scope.engagements[engagement][validity] = true;
						$scope.engagements[engagement]['display'] = true;
						$scope.engagements[engagement]['visible'] = true;
					}
					state = true;
					return state;
				},function(error){
					if(!state){ return $q.reject(false); }else{ return false;}
				}));
			});
			return $q.all(prom).then(function (result) {
				return result;
			});
		};
		
		$scope.empDetailsLoad = function(){
			empFactory.empHeaders().then(function(response) {
				$scope.tables = response;
				$scope.cleanUpEmpData();
				$scope.workFlowMoveManyFlag.details = false;
				$scope.workFlowMoveManyFlag.rolesFound = false;

				var prom = [];
				angular.forEach($scope.engagements, function(role, key){
					prom.push(loadEngagements(_this.empUUID, key).then(function(response){
						$scope.workFlowMoveManyFlag.details = true;	
					}, function(error){
					}));
				});

				$q.all(prom).then(function (result) {
					if(!$scope.workFlowMoveManyFlag.details){
						$scope.workFlowMoveManyFlag.rolesFound = true; // No roles found
					}
				});
			});
		};

		$scope.onChangeSelectAll = function(selectAll){
			angular.forEach($scope.originalOrgUnitEngagements, function(row, index) {					
				row.selected = selectAll;					
			});
		};

	    $scope.isEnhead = false;
	    $scope.enHeadUnits = false;
	    $scope.isOverEnhead = false;
	    $scope.overEnHeadUnits = false
	   
	    $scope.onClickEnhead = function(){
	      $scope.isEnhead = true;
	      $scope.selectedEnhead = null;
	      $scope.isOverEnhead = false;
	    };

	    $scope.onClickOverEnhead = function(){
	      $scope.isOverEnhead = true;	
	      $scope.selectedOverEnhead = null;
	      $scope.isEnhead = false;
	    };


	    $scope.onChangeOccured = function(val, calledFrom){
	    	
	    	if(val.length>=3){  

	    		if(calledFrom === 'overEnhead'){
	    			$scope.selectedOverEnhead = null;

	    		}else{
	    			$scope.selectedEnhead = null;
	    			$scope.enHeadUnits = true;
	    		}

	    		var o = sysService.orgList.get();
		    	return $http.get('o/'+o[0].uuid+'/full-hierarchy', 
		    		{ params: { query: val, 'effective-date': $scope.empMoveDate}}
		    	).then(function(response){
		    		var resData = response.data;   
		    		$scope.$broadcast("typeAheadData", [resData.hierarchy]);
		    		$scope.enHeadUnits = $scope.overEnHeadUnits = false;
		    	});
	    	}
	    };

	   
        
    	$scope.selectNode = function(node,calledFrom){
    		if(calledFrom === 'overEnhead'){
    			$scope.valueOverEnhead = node.name;
    			$scope.selectedOverEnhead = node;
    			$scope.org_unit = node;
    		}else{
    			$scope.valueEnhead = $scope.orgSelectedName = node.name;
    			$scope.selectedEnhead = node;
    			$scope.original_org_unit = node;
    		}
        	
        };

        $scope.$on("hideTypeAheadTree", function(event){
    		$scope.isEnhead = $scope.isOverEnhead = false; 
    	});

		// Modal handler code begins ////////////////////////////////////////////////////////////
		$scope.overwriteFutureEngagements = 1;
		$scope.openMoveConfirmDialog = function () {
			var modalInstance = $modal.open({
				templateUrl: sysService.path+'partials/employee/modalEmployeeMovePopup.html',
				controller: ModalInstanceCtrl,
				windowClass: 'employeeMoveManyFutureConfirm',
				resolve: {
					message: function () {
						return "Employee Roles";
					}
				}
			});

			modalInstance.result.then(function (selectedMessage) {
				$scope.overwriteFutureEngagements = selectedMessage;
				$scope.moveEmpRoles();
			}, function () {
			});
		};

		var ModalInstanceCtrl = function ($scope, $modalInstance, message) {

			$scope.message = message;

			$scope.ok = function (msg) {
				$modalInstance.close(msg);
			};

			$scope.cancel = function () {
				$modalInstance.dismiss('cancel');
			};
		};
		// Modal handler code ends ////////////////////////////////////////////////////////////

		$scope.currentRole; 
		$scope.empMoveRow = function(role){
			$scope.currentRole = role;

			// check for future role only
			var isFutureRolePresent = false;
			angular.forEach($scope.tables[role].tr.future, function(row, index){
				if(row.selected){
					isFutureRolePresent = true;
				}
			})

			if(isFutureRolePresent)
				$scope.openMoveConfirmDialog();
			else
				$scope.moveEmpRoles();
		};

		$scope.moveEmpRoles = function() {
			var role = $scope.currentRole;
			$scope.engagements[role].data['present'] = [];
			$scope.engagements[role].data['future'] = [];
			$scope.workFlowMoveManyFlag.moved = false;
			var futureSplit = false;
			//handling present engagements
			angular.forEach($scope.tables[role].tr.present, function(row, index){
				if(row.selected){
					$scope.workFlowMoveManyFlag.moved = true;
					row.overwrite = 1;
					var insertRow = _.clone(row);
					var mkeDate = $scope.empMoveDate;
						var parts = mkeDate.split("-");
						var dt = new Date();
						dt.setDate(parseInt(parts[0]));
						dt.setMonth(parseInt(parts[1])-1);
						dt.setYear(parseInt(parts[2]));
						dt.setDate(dt.getDate()-1);

						mkeDate = $filter('date')(dt, 'dd-MM-yyyy');
						insertRow['org-unit'] = $scope.org_unit;
						insertRow['valid-from'] = $scope.empMoveDate;
						$scope.engagements[role].data['present'].push(insertRow);
				}
			})

			//handling future engagements
			angular.forEach($scope.tables[role].tr.future, function(row, index){
				if(row.selected){
					$scope.workFlowMoveManyFlag.moved = true;
					row.overwrite = ($scope.overwriteFutureEngagements == 'yes') ? 1:0;

					if($scope.overwriteFutureEngagements == 'yes'){ // Do nothing
						var insertRow = _.clone(row);
						insertRow['org-unit'] = $scope.org_unit;
						insertRow['valid-from'] = $scope.empMoveDate;
						$scope.engagements[role].data['future'].push(insertRow);
					}else if($scope.overwriteFutureEngagements == 'no'){ // Append a row with days duration
						var insertRow = _.clone(row);
						insertRow['org-unit'] = $scope.org_unit;
						if(!futureSplit){
							var newRow = _.clone(insertRow);
							newRow['uuid'] = 'NULL';
							newRow['valid-from'] = $scope.empMoveDate;
							var mkeDate = insertRow['valid-from']
							var parts = mkeDate.split("-");
							var dt = new Date();
							dt.setDate(parseInt(parts[0]));
							dt.setMonth(parseInt(parts[1])-1);
							dt.setYear(parseInt(parts[2]));
							dt.setDate(dt.getDate()-1);

							mkeDate = $filter('date')(dt, 'dd-MM-yyyy');
							newRow['valid-to'] = mkeDate;
							$scope.engagements[role].data['future'].push(newRow);
							//////////////////////////////////////////////////////
							insertRow['valid-from'] = insertRow['valid-from'];
							insertRow['org-unit'] = row['org-unit'];
							futureSplit = true;
						}
						$scope.engagements[role].data['future'].push(insertRow);
					}
				}
			})
			$scope.engagements[role].moved = true;
		};

		$scope.empMoveConfirm = function(){
			var data = {"presentEngagementIds":[], "futureEngagementIds":[], "presentRoleIds":[], "futureRoleIds":[]};
			var prom = [];
	            prom.push(angular.forEach($scope.engagements, function(value, index){
						if(index == 'engagement'){
							prom.push(angular.forEach(value.data, function(keyValue, keyIndex){
								prom.push(angular.forEach(keyValue, function(v, i){
									if(keyIndex == "present"){
										data['presentEngagementIds'].push({'uuid': v.uuid, 'overwrite':v.overwrite});
									}else if(keyIndex == "future"){
										if(v.uuid != "NULL"){
											data['futureEngagementIds'].push({'uuid': v.uuid, 'overwrite':v.overwrite});
										}
									}
								}))
							}));
						}else{
							prom.push(angular.forEach(value.data, function(keyValue, keyIndex){
								prom.push(angular.forEach(keyValue, function(v, i){
									if(keyIndex == "present"){
										data['presentRoleIds'].push({'uuid': v.uuid, 'overwrite':v.overwrite});
									}else if(keyIndex == "future"){
										if(v.uuid != "NULL"){
											data['futureRoleIds'].push({'uuid': v.uuid, 'overwrite':v.overwrite});
										}
									}
								}))
							}));
						}
					})
				);
	        $q.all(prom).then(function () {
	        	empFactory.empMove(_this.empUUID, $scope.empMoveDate, $scope.org_unit.uuid, data, function(status, data){
					if(status){
						$scope.workFlowMoveManyFlag.success = true;
						$scope.cleanUpEmpData();
						$scope.loadNextEmployeeOrClose();
					}else{
						$scope.workFlowMoveManyFlag.fail = true;
						$scope.workFlowMoveManyFlag.failMessage = data.errors;
					}
				});
	        });

		}

		$scope.setCurrentEmployee = function() {
			var engagementsLength = $scope.transferOrgUnitEngagements.length;

			if($scope.currentEmpCounter < engagementsLength){
				_this.empUUID = $scope.transferOrgUnitEngagements[$scope.currentEmpCounter]['person']; //['uuid'];
				$scope.empName = $scope.transferOrgUnitEngagements[$scope.currentEmpCounter]['person-name'];
			}
			$scope.currentEmpCounter++;

			return ($scope.currentEmpCounter <= engagementsLength); 

		};
		
		$scope.loadNextEmployeeOrClose = function() {
			var currentEmployeeExists = $scope.setCurrentEmployee();
			if(currentEmployeeExists){
				$scope.empDetailsLoad();
			}else{
				// sysService.recordEvent.set('success', 'Employee moved successfully');
				sysService.recordEvent.set('success', sysService.i18n('employeeMoveMany_employee_moved_successfully_label'));
				$scope.$parent.empMoveManyModal('close');
			}			
		};


		$scope.dateSelect = function(dateField){
			var date = $scope[dateField];
			if(sysService.dateFormat.validateInput(date)){
				date = $filter('date')(date, 'dd-MM-yyyy');
				$scope[dateField] = date;
				$scope.empStartMoveDate = date;
				$scope.$broadcast('dateSelected',date);
				if($scope.empStartMoveDate != "" && $scope.original_org_unit != "" && angular.isDefined($scope.original_org_unit)){
					$scope.loadEngagementsForSelectedOrgUnit();
				}
			}
		}

		$scope.open = function($event, datePicker) {
			$event.preventDefault();
			$event.stopPropagation();
			$scope[datePicker] = ($scope[datePicker])?false:true;
		};

	}]);