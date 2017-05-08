'use strict';
/* Employee controllers */ 

angular.module('moApp.controllers').
	controller('employeeAbsence',["$scope", 'empFactory', "$filter", "$rootScope", '$http', 'sysService', '$q', 'hotkeys', function($scope, empFactory, $filter, $rootScope, $http, sysService, $q, hotkeys) {
		$scope.workFlowAbsenceFlag = {
			invalid : false,
			found : false,
			notFound : false,
			fail : false,
			success : false,
			details : false,
			rolesNotFound: false
		};

		$scope.empRoles = {
			"engagement":{ "key": "engagement", "name": "Engagement", "visible":false, data: []}
		};
		$scope.selectAll = false;
		$scope.absenceTypes = {};
		$scope.empAbsenceDate;
		$scope.empAbsenceEndDate;
		$scope.tables = {};
		$http.get('/mo/role-types/absence/facets/type/classes/').then(function(response) {
			$scope.absenceTypes = response.data;
		});

		$scope.cleanUpEmpData = function(){
			angular.forEach($scope.empRoles, function(role, key){
				role.visible = false;
				role.data = [];
			});
			angular.forEach($scope.tables, function(row, key){
				angular.forEach($scope.engagements, function(role, key){
					row.tr[role] = [];
				});
			});
		};

		$scope.empCPRSearch = function(){
			$scope.cleanUpEmpData();
			$scope.workFlowAbsenceFlag = {
				invalid : false,
				found : false,
				notFound : false,
				fail : false,
				success : false,
				details : false,
				rolesNotFound: false
			};
			empFactory.empHeaders().then(function(response) {
				$scope.tables = response;
			});
			if(angular.isDefined(this.empCPR) && this.empCPR != ""){
				empFactory.empInfosByCPR(this.empCPR).then(function(response){
					$scope.workFlowAbsenceFlag.found = true;
					$scope.employee = response;
					$scope.empUUID = response["uuid"];
				},function(error){
					$scope.workFlowAbsenceFlag.notFound = true;
				});
			}else{
				$scope.workFlowAbsenceFlag.invalid = true;
			}
		}

        $scope.setAbsenceType = function(obj) {
			$scope.absenceType = obj.absenceType;
		};

		$scope.$watch('absenceType', function(newVal){
        	if(angular.isDefined(newVal) && newVal != "" && newVal !== null){
        		if(angular.isDefined($scope.empAbsenceDate) && $scope.empAbsenceDate != ""){ 
					console.log("Fetch emp details with ", $scope.empAbsenceDate, ' with absence', newVal);
        			loadEngagements();
        		}
        	}
        })
        
		var loadEngagements = function(start, end){
			$scope.cleanUpEmpData();
			$scope.workFlowAbsenceFlag.details = false;
			$scope.empAbsenceDate = $filter('date')($scope.empAbsenceDate, 'dd-MM-yyyy');
			$scope.empAbsenceEndDate = $filter('date')($scope.empAbsenceEndDate, 'dd-MM-yyyy');

			var prom = [];
			var found = false;
			$scope.workFlowAbsenceFlag.rolesNotFound = false;
			angular.forEach($scope.empRoles, function(engagement, key){
				prom.push(empFactory.empRoles($scope.empUUID, key, $scope.empAbsenceDate).then(function(response) {
					$scope.empRoles[key].data = response;
					$scope.empRoles[key].visible = true;
					found = true;
				},function(error){
					$scope.empRoles[key].data = [];
					$scope.empRoles[key].visible = false;
				}));
			});

			$q.all(prom).then(function (result) {
				if(found){
					$scope.workFlowAbsenceFlag.rolesNotFound = false;
					$scope.workFlowAbsenceFlag.details = true;
				}else{
					$scope.workFlowAbsenceFlag.rolesNotFound = true;
				}
			});
		}
		
		var absenceList = [];
		$scope.countCheckedAbsence = function(){
			var prom = [];
			absenceList = [];
			prom.push(angular.forEach($scope.empRoles, function(value, index){
				angular.forEach(value.data, function(item, index){
					if (item.selected) {
						var absence = {
										'role-type': 'absence',
										'related-role': {'uuid' : item.uuid}, 
										'type': {'uuid':$scope.absenceType}, 
										'valid-from': $scope.empAbsenceDate,
										'valid-to': $scope.empAbsenceEndDate};
						absenceList.push(absence);
					}
				});
			}));
			$q.all(prom).then(function (result) {
				console.log(absenceList);
				return absenceList;
			});
		}
		$scope.empAbsenceConfirm = function(){
			if (absenceList.length > 0)	{					
				$http.post("/mo/e/"+$scope.empUUID+"/actions/absence", JSON.stringify(absenceList)).
					success(function(data, status, headers, config) {
						if(sysService.state.data.page.key == "employee" && sysService.state.data.page.subKey == "detail"){
							var deferred = $q.defer();
							var promise = deferred.promise;
							promise.then(function () {
								$scope.$parent.loadEngagements($scope.empUUID, 'absence');
							}).then(function () {
								$scope.workFlowAbsenceFlag.success = true;
								sysService.recordEvent.set('success', sysService.i18n('employee_absence_updated_successfully'));
								$scope.$parent.empAbsenceModal('close');
							});
							deferred.resolve();
						}else{
							$scope.workFlowAbsenceFlag.success = true;
							sysService.recordEvent.set('success', sysService.i18n('employee_absence_updated_successfully'));
							$scope.$parent.empAbsenceModal('close');
						}
					}).
					error(function(data, status, headers, config) {
						$scope.workFlowAbsenceFlag.fail = true;						
					});
			}
		}

		$scope.isApplyBtnDisabled = function (){
			if(absenceList.length >=1){ return false; }
			return true;
		};

		$scope.selectAllRoles = function() {
			$scope.selectAll = !$scope.selectAll;
			angular.forEach($scope.empRoles, function(value, index){
				angular.forEach(value.data, function(item, index){
					item.selected = $scope.selectAll;
					$scope.countCheckedAbsence();
				});
			});
		};

		$scope.dateSelect = function(dateField){
			var date = $scope[dateField];
			if(sysService.dateFormat.validateInput(date)){
				$scope[dateField] = date;
				if(dateField == "empAbsenceDate" && $scope.empAbsenceDate != "" && $scope.absenceType != "" && angular.isDefined($scope.absenceType)){ loadEngagements(); }
			}
		}

		$scope.open = function($event, datePicker) {
			$event.preventDefault();
			$event.stopPropagation();
			$scope[datePicker] = ($scope[datePicker])?false:true;
		};

		hotkeys.add({
			combo: sysService.shortcuts.popupSubmit.key,
			description: sysService.shortcuts.popupSubmit.title,
			callback: function() {
				if($scope.empDetails) $scope.empAbsenceConfirm();
			}
		});
		
		hotkeys.add({
			combo: sysService.shortcuts.popupClose.key,
			description: sysService.shortcuts.popupClose.title,
			callback: function() {
				$scope.$parent.empAbsenceModal('close');
			}
		});
	}]);