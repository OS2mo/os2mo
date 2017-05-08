'use strict';
/* Employee controllers */ 

angular.module('moApp.controllers').
	controller('employeeEnd',['$scope', "$filter","empFactory", 'sysService','$q', 'hotkeys', function($scope,$filter,empFactory,sysService,$q, hotkeys){
		$scope.workFlowEndFlag = {
			invalid : false,
			found : false,
			notFound : false,
			fail : false,
			failMessage : {},
			success : false,
			details : false,
			rolesNotFound: false
		}
		$scope.sysService = sysService;

        $scope.validity = ['present', 'past', 'future'];
		$scope.engagements = {
			"engagement":{ "key": "engagement", "visible":false, data: []},
			"association":{"key": "association", "visible":false, data: []},
			"it":{"key": "it", "visible":false, data: []},
			"contact":{"key": "contact", "visible":false, data: []},
			"job-function":{"key": "job-function", "visible":false, data: []},
			"leader":{"key": "leader", "visible":false, data: []},
			"absence":{"key": "absence", "visible":false, data: []}
        }

		$scope.empCPRSearch = function(){
			$scope.workFlowEndFlag = {
				invalid : false,
				found : false,
				notFound : false,
				endFail : false,
				endSuccess : false,
				details : false,
				rolesNotFound: false
			}
	        empFactory.empHeaders().then(function(response) {
				$scope.tables = response;
			});
			if(typeof (this.empCPR) !== "undefined" && this.empCPR != ""){					
				empFactory.empInfosByCPR(this.empCPR).then(function(response){
						$scope.workFlowEndFlag.found = true;
						$scope.employee = response;
						$scope.empUUID = response["uuid"];
					}, function(error){
						$scope.workFlowEndFlag.notFound = true;
				});
			}else{
				$scope.workFlowEndFlag.invalid = true;
			}
		};

		var loadEngagements = function(uuid, date){
			var prom = [];
			var found = false;
			$scope.workFlowEndFlag.rolesNotFound = false;
			angular.forEach($scope.engagements, function(engagement, key){
				prom.push(empFactory.empRoles(uuid, key, date, '').then(function(response){
					$scope.engagements[key].data = response;
					$scope.engagements[key].visible = true;
					found = true;
				},function(error){
					$scope.engagements[key].data = [];
					$scope.engagements[key].visible = false;
				}));
			});

			$q.all(prom).then(function (result) {
				if(found){
					$scope.workFlowEndFlag.rolesNotFound = false;
					$scope.workFlowEndFlag.details = true;
				}else{
					$scope.workFlowEndFlag.rolesNotFound = true;
				}
			});
		};

		$scope.empEndConfirm = function(){
			empFactory.empEnd($scope.empUUID, $scope.empEndDate,function(status, data){
				if(status){
					if(sysService.state.data.page.key == "employee" && sysService.state.data.page.subKey == "detail"){
						var deferred = $q.defer();
						var promise = deferred.promise;
						promise.then(function () {
							angular.forEach($scope.engagements, function(role, key){
								$scope.$parent.loadEngagements($scope.empUUID, key);
							});
						}).then(function () {
							$scope.workFlowEndFlag.success = true;
							sysService.recordEvent.set('success', sysService.i18n('employee_terminated_successfully_label'));
							$scope.$parent.empEndModal('close');
						});
						deferred.resolve();
					}else{
						$scope.workFlowEndFlag.success = true;
						sysService.recordEvent.set('success', sysService.i18n('employee_terminated_successfully_label'));
						$scope.$parent.empEndModal('close');
					}
				}else{
					$scope.workFlowEndFlag.fail = true;
					$scope.workFlowEndFlag.failMessage = data.errors;
				}
			});
		}

		$scope.dateSelect = function(dateField){
			var date = $scope[dateField];
			if(sysService.dateFormat.validateInput(date)){
				date = $filter('date')(date, 'dd-MM-yyyy');
				$scope[dateField] = date;

				var prom = [];
				prom.push(angular.forEach($scope.empRoles, function(value, index){
					$scope.empRoles[index].data = [];
					$scope.empRoles[index].visible = false;
				}));
				$q.all(prom).then(function (result) {
					loadEngagements($scope.empUUID, date);
				});
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
				if($scope.empDetails) $scope.empEndConfirm();
			}
		});
		
		hotkeys.add({
			combo: sysService.shortcuts.popupClose.key,
			description: sysService.shortcuts.popupClose.title,
			callback: function() {
				$scope.$parent.empEndModal('close');
			}
		});

	}]);