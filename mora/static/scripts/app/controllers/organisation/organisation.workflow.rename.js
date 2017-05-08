'use strict';
/* organisation controllers */ 

angular.module('moApp.controllers').
	controller('organisationRename',['$scope', "$filter","orgFactory", 'sysService', 'hotkeys', '$state', function($scope,$filter,orgFactory,sysService, hotkeys, $state){
		$scope.workFlowRenameFlag = {
			invalid: false,
			listFound : false,
			listFoundError : false,
			uuidSelected : false,
			renameFail : false,
			renameFailMessage : {},
			renameSuccess : false
		}
		$scope.sysService = sysService;
		$scope.orgUnitList = {};
		
		if(sysService.state.data.page.key == "organisation" && sysService.state.data.page.subKey == "detail"){
			$scope.orgUnitSearchStr = $scope.$parent.organisation.name;
		}else{
			$scope.orgUnitSearchStr = '';
		}

		$scope.isApplyBtnDisabled = function (){
			if(typeof($scope.orgUnitName) !== "undefined" && $scope.orgStartRenameDate){
				return false;
			}
			return true;
		};

		$scope.orgUUIDSearch = function(){
			if(typeof (this.orgUnitSearchStr) !== "undefined" && this.orgUnitSearchStr != ""){					
				$scope.workFlowRenameFlag = {
					invalid: false,
					listFound : false,
					listFoundError : false,
					uuidSelected : false,
					renameFail : false,
					renameSuccess : false
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
						$scope.workFlowRenameFlag.listFound = true;
            		},
                	function(error){
                		$scope.orgUnitList = {};
                		$scope.workFlowRenameFlag.listFoundError = true;
                	}
	            );
			}else{
				$scope.workFlowRenameFlag.invalid = true;
			}
		};

		$scope.selectOrgUUID = function(uuid, date){
			orgFactory.orgInfos(uuid, date).then(function(response){	
				response 				 = response[0];
				$scope.orgUnit 	 		 = response;
				$scope.orgUUID 			 = response["uuid"]; 
				$scope.orgUnitName       = response.name;

				$scope.workFlowRenameFlag.uuidSelected = true;
				$scope.workFlowRenameFlag.listFound = false;
				sysService.recordEvent.set('debug', 'organisation-unit found');
			}, function(error){
				sysService.recordEvent.set('debug', 'Error fetching the organisation UUID');
			});
		};

		$scope.renameOrgName = function(str){ $scope.orgUnitName = str; };

		$scope.orgRenameConfirm = function(){
			$scope.orgUnit.name = $scope.orgUnitName;
			$scope.orgUnit['valid-from'] = $scope.orgStartRenameDate;
			$scope.orgUnit['valid-to'] = $scope.orgStopRenameDate;
			var data = $scope.orgUnit;
			orgFactory.orgRename($scope.orgUnit.org, $scope.orgUUID, data, function(status, data){
				if(status){
					$scope.workFlowRenameFlag.renameSuccess = true;
					sysService.recordEvent.set('success', sysService.i18n('organisation_renamed_successfully').replace("%UUID%", $scope.orgUUID));
					if(sysService.state.data.page.key == "organisation" && sysService.state.data.page.subKey == "detail"){
						$state.go($state.current, {}, {reload: true});
					}
					$scope.$emit('reloadTree', true);
					$scope.$parent.orgRenameModal('close');
				}else{
					$scope.workFlowRenameFlag.renameFail = true;
					$scope.workFlowRenameFlag.renameMessage = data.errors;
				}
			});
			
		};

		$scope.open = function($event, datePicker) {
			$event.preventDefault();
			$event.stopPropagation();
			$scope[datePicker] = ($scope[datePicker])?false:true;
			console.log(datePicker, $scope[datePicker])
		};

		$scope.dateSelect = function(dateField){
			var date = $scope[dateField];
			if(sysService.dateFormat.validateInput(date)){
				date = $filter('date')(date, 'dd-MM-yyyy');
				$scope[dateField] = date;
				console.log("date", $scope[dateField]);
			}
		}

		hotkeys.add({
			combo: sysService.shortcuts.popupSubmit.key,
			description: sysService.shortcuts.popupSubmit.title,
			callback: function() {
				if($scope.isApplyBtnDisabled()) $scope.orgRenameConfirm();
			}
		});
		
		hotkeys.add({
			combo: sysService.shortcuts.popupClose.key,
			description: sysService.shortcuts.popupClose.title,
			callback: function() {
				if(angular.isDefined($scope.$parent.orgRenameModalOpen)){ $scope.$parent.orgRenameModal('close'); }
			}
		});
	}]);