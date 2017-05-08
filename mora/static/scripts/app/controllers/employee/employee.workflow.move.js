'use strict';
/* Employee controllers */ 

angular.module('moApp.controllers').
	controller('employeeMove',["$scope", 'empFactory', "$filter", "$rootScope", '$http', '$modal', 'filterFilter', 'sysService', '$q', 'hotkeys', function($scope, empFactory, $filter, $rootScope, $http, $modal, filterFilter, sysService, $q, hotkeys) {
		$scope.workFlowMoveFlag = {
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
			rolesFound: false
		};
		var _this = this;
		$scope.empUUID;
		$scope.empName;
		$scope.org_unit;
		$scope.empMoveDate;
		$scope.tables;
		$scope.org_unit;
		$scope.rEngagement = [];

		$scope.originalOrgUnitEngagementsFound = false;
		$scope.originalOrgUnitEngagements;
		$scope.transferOrgUnitEngagements = [];
		$scope.currentEmpCounter = 0;

		$scope.validity = ['present', 'future'];
		$scope.engagements = {
			"engagement":{ "key": "engagement", "name": "Engagement", "visible":false, "data": { "present": [], "future": [] }, defaultTab: 'present'},
			"association":{ "key": "association", "name": "Association", "visible":false, "data": { "present": [], "future": [] }, defaultTab: 'present'}
        };

        $scope.setRelatedEngagement = function(uuid, obj){
        	if(obj){
        		$scope.rEngagement.push(uuid)	
        	}else{
        		$scope.rEngagement = _.without($scope.rEngagement, uuid)
        		angular.forEach($scope.validity, function(state, key){
        			angular.forEach($scope.tables['association'].tr[state], function(value, key){
        				console.log(value)
        				if(value['related-engagement'].uuid == uuid){
        					value.selected = false;
        				}
        			})
        		})
        		
        	}
        	
        }
        $scope.empCPRSearch = function(){
			$scope.cleanUpEmpData();
			$scope.workFlowMoveFlag = {
				invalid : false,
				found : false,
				notFound : false,
				fail : false,
				success : false,
				moved : false,
				details : false,
				infoLoaded: false,
				orgUnitFromFound: false,
				orgUnitFromResultFound: false,
				orgUnitToFound: false,
				rolesFound: false
			};
			$scope.empMoveDate = null;
			empFactory.empHeaders().then(function(response) {
				$scope.tables = response;
			});
			if(angular.isDefined(this.empCPR) && this.empCPR != ""){
				empFactory.empInfosByCPR(this.empCPR).then(function(response){
					$scope.workFlowMoveFlag.found = true;
					$scope.employee = response;
					$scope.empUUID = response["uuid"];
				},function(error){
					$scope.workFlowMoveFlag.notFound = true;
				});
			}else{
				$scope.workFlowMoveFlag.invalid = true;
			}
		}

		$scope.cleanUpEmpData = function(){
			angular.forEach($scope.engagements, function(role, key){
				role.visible = false;
				role.data = { "present": [], "future": [] };
			});
			angular.forEach($scope.tables, function(row, key){
				angular.forEach($scope.engagements, function(role, key){
					row.tr[role] = [];
					row.tr[role]['visible'] = true;
				});
			});
		};


		$scope.$watch('org_unit', function(newVal){
        	if(angular.isDefined(newVal) && newVal != ""){
        		if($scope.empMoveDate != "" && $scope.org_unit != "" && angular.isDefined($scope.org_unit)){
					$scope.empDetailsLoad();
				}
        	}
        })

		var activeEngagement = false;
		var loadEngagements = function(cpr, engagement){
			var prom = [];
			var table = $scope.tables[engagement];
			var defaultTab = '';
			var visible = false;
			var state = false;
			$scope.workFlowMoveFlag.moved = false;

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
			$scope.cleanUpEmpData();
			$scope.workFlowMoveFlag.details = false;
			$scope.workFlowMoveFlag.rolesFound = false;

			var prom = [];
			angular.forEach($scope.engagements, function(role, key){
				prom.push(loadEngagements($scope.empUUID, key).then(function(response){
					$scope.workFlowMoveFlag.details = true;	
				}, function(error){
				}));
			});

			$q.all(prom).then(function (result) {
				if(!$scope.workFlowMoveFlag.details){
					$scope.workFlowMoveFlag.rolesFound = true; // No roles found
				}
			});
		};

		$scope.onChangeSelectAll = function(selectAll){
			angular.forEach($scope.originalOrgUnitEngagements, function(row, index) {					
				row.selected = selectAll;					
			});
		}

		// Modal handler code begins ////////////////////////////////////////////////////////////
		$scope.overwriteFutureEngagements = 1;
		$scope.openMoveConfirmDialog = function () {
			var modalInstance = $modal.open({
				templateUrl: sysService.path+'partials/employee/modalEmployeeMovePopup.html',
				controller: ModalInstanceCtrl,
				windowClass: 'employeeMoveFutureConfirm',
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
			$scope.workFlowMoveFlag.moved = false;
			var futureSplit = false;
			//handling present engagements
			angular.forEach($scope.tables[role].tr.present, function(row, index){
				if(row.selected){
					$scope.workFlowMoveFlag.moved = true;
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
					$scope.workFlowMoveFlag.moved = true;
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
	        	empFactory.empMove($scope.empUUID, $scope.empMoveDate, $scope.org_unit.uuid, data, function(status, data){
					if(status){
						if(sysService.state.data.page.key == "employee" && sysService.state.data.page.subKey == "detail"){
							var deferred = $q.defer();
							var promise = deferred.promise;
							promise.then(function () {
								angular.forEach($scope.engagements, function(role, key){
									$scope.$parent.loadEngagements($scope.empUUID, key);
								});
							}).then(function () {
								$scope.workFlowMoveFlag.success = true;
								sysService.recordEvent.set('success', sysService.i18n('employee_moved_successfully_label'));
								$scope.$parent.empMoveModal('close');
							});
							deferred.resolve();
						}else{
							$scope.workFlowMoveFlag.success = true;
							sysService.recordEvent.set('success', sysService.i18n('employee_moved_successfully_label'));
							$scope.$parent.empMoveModal('close');
						}
					}else{
						$scope.workFlowMoveFlag.fail = true;
						$scope.workFlowMoveFlag.failMessage = data.errors;
					}
				});
	        });
		}

		$scope.dateSelect = function(dateField){
			var date = $scope[dateField];
			if(sysService.dateFormat.validateInput(date)){
				date = $filter('date')(date, 'dd-MM-yyyy');
				$scope[dateField] = date;
				$scope.empMoveDate = date;
				$scope.$broadcast('dateSelected',date);
				if($scope.empMoveDate != "" && $scope.org_unit != "" && angular.isDefined($scope.org_unit)){
					$scope.empDetailsLoad();
				}
			}
		}

		$scope.open = function($event, datePicker) {
			$event.preventDefault();
			$event.stopPropagation();
			$scope[datePicker] = ($scope[datePicker])?false:true;
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
    	    		{ params: { query: val, 'effective-date': $scope.empMoveDate}}
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
			$scope.org_unit = node;	
        };

        $scope.$on("hideTypeAheadTree", function(event){
    		$scope.isEnhead = false; 
    	});

	}]);