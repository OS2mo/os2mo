'use strict';
/* Organisation controllers */

angular.module('moApp.controllers').
	controller('moTimemachine',["$scope", "$http", "$filter", "$modal", "orgFactory", "$location", "sysService", "$q", "hotkeys",function($scope, $http, $filter, $modal, orgFactory, $location, sysService, $q, hotkeys) {
		$scope.sysService = sysService;

		hotkeys.add({
			combo: sysService.shortcuts.popupClose.key,
			description: sysService.shortcuts.popupClose.title,
			callback: function() {
				window.self.close();
			}
		});
	}])
	.controller('moTimemachineBlock',["$scope", "$http", "$filter", "$modal", "orgFactory", "$location", "sysService", "$q",function($scope, $http, $filter, $modal, orgFactory, $location, sysService, $q) {
		$scope.effectiveDate;
		////////////////////////////////////////////////////////////////////////////////
		$scope.flag = {
	  		orgFound: false,
	  		orgInfoLoaded: false,
	  		orgEngagementsFound: false,
	  		orgEngagementsLoaded: false,
	  		orgEdit: false,
	  		orgEditSuccess: false,
	  		orgCreate: false,
	  		orgCreateSuccess: false,
	  		dataUpdated: false,
	  		dataAdded: false
	  	};
	  	$scope.orgUUID;
	  	$scope.visibleEngagementCount = 0;
	  	$scope.validity = ['present'];
		$scope.engagements = {
			"org-unit":{ "key": "org-unit", "visible":false}, // Editable
			"location":{"key": "location", "visible":false}, // Editable
			"contact-channel":{"key": "contact-channel", "visible":false}, // Editable
			"leader":{"key": "leader", "visible":false}, // Non editable
			"engagement":{"key": "engagement", "visible":false}, // Non editable
			"association":{"key": "association", "visible":false}, // Non editable
			"job-function":{"key": "job-function", "visible":false} // Non editable
        };
        var active = false;

        var activeEngagement = false;
		$scope.loadEngagements = function(uuid, engagement, date){
			var prom = [];
			var table = $scope.tables[engagement];
			var defaultTab = '';
			var visible = false;
			
			$scope.engagements[engagement]['visible'] = visible;
			angular.forEach($scope.validity, function(validity, position){
				table.tr[validity] = [];
				$scope.engagements[engagement][validity] = false; 
				prom.push(orgFactory.orgRoles(uuid, engagement, date, validity).then(function(response){
					table.tr[validity] = [];
					table.tr[validity] = response;
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
							$scope.flag.orgEngagementsFound = true;
						}
					});
					//$scope.visibleEngagementsCount++;
					$scope.engagements[engagement]['visible'] = true;
					$scope.visibleEngagementsCount++;
				}
			});
		};

		$scope.initOrgData = function (uuid, date){
			uuid = (angular.isDefined(uuid))?uuid:$scope.orgUUID;
			date = (angular.isDefined(date))?date:$scope.orgEffectiveDate;
   			orgFactory.orgInfos(uuid, date).then(function(response){
				response = response[0];
				$scope.organisation = response;
				$scope.orgUUID = response["uuid"]; 
				$scope.visibleEngagementsCount = 0;
				$scope.flag.orgFound = true;
				$scope.flag.orgInfoLoaded = true;
				active = false;
				angular.forEach($scope.engagements, function(role, key){
					$scope.loadEngagements(uuid, key, date);
				});
   				//$scope.loadEngagements(uuid);
			}, function(error){
				$scope.flag.orgFound = false;
				$scope.flag.orgInfoLoaded = true;
			});
		};

		$scope.cleanUpOrgData = function(){
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
		$scope.dateSelect = function(dateField){
			var date = $scope[dateField];
			if(sysService.dateFormat.validateInput(date)){
				$scope.effectiveDate = $filter('date')(date, 'dd-MM-yyyy');
				$scope.$broadcast("timeMachineDateSelected", date)
				$scope.cleanUpOrgData();
			}
		}
		$scope.open = function($event, datePicker) {
			$event.preventDefault();
			$event.stopPropagation();
			$scope[datePicker] = ($scope[datePicker])?false:true;
		};


		$scope.organizations = [];
		$scope.orgUnits = [];

		// Load Orgs and OrgUnits
		sysService.orgList.fetch().then(function(response){
			$scope.organizations = response;
			sysService.loadOrgData.getUnits().then(function(response) {
	            $scope.orgUnits = response;
	        }, function(error){ // No child units
	        });
		});
		
		$scope.selectNode = function(node){
			$scope.selectedOrgUnit = node;
			orgFactory.orgHeaders().then(function(response) {
				$scope.cleanUpOrgData();
				$scope.tables = response;
				$scope.initOrgData(node.uuid, $scope.effectiveDate);
			});
	    };

        $scope.$on("timeMachineDateSelected", function(event, date){
			var date = $filter('date')(date, 'dd-MM-yyyy');
			sysService.orgUnitList.fetch(date, 'treeType').then(function(response){
                angular.forEach($scope.organizations,function(value, key){
                	$scope.$broadcast("timemachineTypeAheadData", {'response': response[value.uuid], 'date': date});
                });
            }, function(error){ // No child units
	        });
	    });

	}]);