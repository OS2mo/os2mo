'use strict';
/* Employee controllers */ 

angular.module('moApp.controllers').
	controller('organisationEnd',['$scope', "$filter","orgFactory", 'sysService','$q', 'hotkeys', function($scope,$filter,orgFactory,sysService,$q, hotkeys){
		$scope.workFlowEndFlag = {
			invalid : false,
			listFound : false,
			listFoundError : false,
			uuidSelected : false,
			
			endFail : false,
			endFailMsg : '',
			endSuccess : false,
			details : false,
			rolesNotFound: false
		}
		$scope.sysService = sysService;

		if(sysService.state.data.page.key == "organisation" && sysService.state.data.page.subKey == "detail"){
			$scope.orgUnitSearchStr = $scope.$parent.organisation.name;
		}else{
			$scope.orgUnitSearchStr = '';
		}

        $scope.validity = ['past', 'present', 'future'];
		$scope.engagements = {
			"org-unit":{ "key": "org-unit", "visible":false, data: []},
			"location":{"key": "location",  "visible":false, data: []},
			"contact-channel":{"key": "contact-channel", "visible":false, data: []},
			"leader":{"key": "leader", "visible":false, data: []},
			"engagement":{"key": "engagement", "visible":false, data: []},
			"association":{"key": "association", "visible":false, data: []},
			"job-function":{"key": "job-function", "visible":false, data: []}
        };

		$scope.orgUUIDSearch = function(){
			if(typeof (this.orgUnitSearchStr) !== "undefined" && this.orgUnitSearchStr != ""){					
				$scope.workFlowEndFlag = {
					invalid : false,
					listFound : false,
					listFoundError : false,
					uuidSelected : false,
					
					endFail : false,
					endSuccess : false,
					details : false,
					rolesNotFound: false
				}
				var customParam = {
		        		"query": this.orgUnitSearchStr
		        	};
		        orgFactory.orgHeaders().then(function(response) {
					$scope.tables = response;
				});
				orgFactory.organisationList(customParam).then(
            		function(response){ 
            			$scope.orgUnitList = response;
						$scope.workFlowEndFlag.listFound = true;
            		},
                	function(error){
                		$scope.orgUnitList = {};
                		$scope.workFlowEndFlag.listFoundError = true;
                	}
	            );
			}else{
				$scope.workFlowEndFlag.invalid = true;
			}
		};

		$scope.selectOrgUUID = function(uuid, date){
			orgFactory.orgInfos(uuid, date).then(function(response){	
				response 				 = response[0];
				$scope.orgUnit 	 		 = response;
				$scope.orgUUID 			 = response["uuid"]; 
				$scope.workFlowEndFlag.uuidSelected = true;
				$scope.workFlowEndFlag.listFound = false;
			}, function(error){
			});
		};

		var loadEngagements = function(uuid, date){
			var prom = [];
			var found = false;
			$scope.workFlowEndFlag.rolesNotFound = false;
			angular.forEach($scope.engagements, function(engagement, key){
				prom.push(orgFactory.orgRoles(uuid, key, date, '').then(function(response){
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
		$scope.orgEndConfirm = function(){
			orgFactory.orgEnd($scope.orgUnit.org, $scope.orgUUID, $scope.orgEndDate,function(status, data){
				if(status){
					if(sysService.state.data.page.key == "organisation" && sysService.state.data.page.subKey == "detail"){
						var deferred = $q.defer();
						var promise = deferred.promise;
						promise.then(function () {
							angular.forEach($scope.engagements, function(role, key){
								$scope.$parent.loadEngagements($scope.orgUUID, key);
							});
						}).then(function () {
							$scope.$emit('reloadTree', true);
							$scope.workFlowEndFlag.success = true;
							sysService.recordEvent.set('success', sysService.i18n('organisation_terminated_successfully').replace("%UUID%", $scope.orgUUID));
							$scope.$parent.orgEndModal('close');
						});
						deferred.resolve();
					}else{
						$scope.$emit('reloadTree', true);
						$scope.workFlowEndFlag.success = true;
						sysService.recordEvent.set('success', sysService.i18n('organisation_terminated_successfully').replace("%UUID%", $scope.orgUUID));
						$scope.$parent.orgEndModal('close');
					}
				}
				else{
					$scope.workFlowEndFlag.endFail = true;
					$scope.workFlowEndFlag.endFailMsg = data.errors;
				}
			});	
		};

		$scope.dateSelect = function(dateField){
			var date = $scope[dateField];
			if(sysService.dateFormat.validateInput(date)){
				$scope.workFlowEndFlag.details = false;
				date = $filter('date')(date, 'dd-MM-yyyy');
				$scope[dateField] = date;

				var prom = [];
				prom.push(angular.forEach($scope.engagements, function(value, index){
					$scope.engagements[index].data = [];
					$scope.engagements[index].visible = false;
				}));
				$q.all(prom).then(function (result) {
					loadEngagements($scope.orgUUID, date);
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
				if($scope.workFlowEndFlag.details) $scope.orgEndConfirm();
			}
		});
		
		hotkeys.add({
			combo: sysService.shortcuts.popupClose.key,
			description: sysService.shortcuts.popupClose.title,
			callback: function() {
				if($scope.$parent.orgEndModalOpen){ $scope.$parent.orgEndModal('close');}
			}
		});

	}]);