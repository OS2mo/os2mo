'use strict';
/* organisation controllers */ 

angular.module('moApp.controllers').
	controller('organisationMove',['$scope', "$filter","orgFactory", 'sysService', 'hotkeys', '$http','$q', function($scope,$filter,orgFactory,sysService, hotkeys, $http, $q){
		var organisationId, orgFromId, orgToId;
		//$scope.orgObj = {};
		$scope.sysService = sysService;
		$scope.orgStartMoveDate;
		$scope.selectedOverEnhead = null;
	    $scope.selectedEnhead = null;
	    $scope.orgSelectedNameHide = false;

	    $scope.orgWorkFlowMoveFlag = {
			fail : false,
			failMessage : {},
			success : false
		}

		//$scope.orgUnits = sysService.orgUnitList.get();

		$scope.orgMoveConfirm = function(){
			orgFactory.orgMove(orgFromId, $scope.orgStartMoveDate, orgToId, organisationId,function(status, data){
				if(status){
					$scope.$emit('reloadTree', true);
					sysService.recordEvent.set('success', sysService.i18n('organisation_moved_successfully'));
					$scope.$parent.orgMoveModal('close');
				}else{
					$scope.orgWorkFlowMoveFlag.fail = true;
					$scope.orgWorkFlowMoveFlag.failMessage = data.errors;
				}
			});
		};

		
		$scope.isApplyBtnDisabled = function (){
			if($scope.selectedOverEnhead != null && $scope.selectedEnhead != null){ 
				return false; 
			}
			return true;
		};

		$scope.dateSelect = function(dateField){
			var date = $scope[dateField];
			if(sysService.dateFormat.validateInput(date)){
				date = $filter('date')(date, 'dd-MM-yyyy');
				$scope[dateField] = date;
			}
		};

		$scope.open = function($event, datePicker) {
			$event.preventDefault();
			$event.stopPropagation();
			$scope[datePicker] = ($scope[datePicker])?false:true;
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
		    		{ params: { query: val, 'effective-date': $scope.orgStartMoveDate}}
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
    			orgToId = node.uuid;
    			organisationId = node.org;
    		}else{
    			$scope.orgSelectedNameHide = false;
    			$scope.valueEnhead = node.name;
    			$scope.selectedEnhead = node;
    			orgFromId = node.uuid;
    			// Get parent org unit
    			if(node.parent != ""){
					orgFactory.orgInfos(node.parent, $scope.orgStartMoveDate).then(function(response){
	            			$scope.orgSelectedName = response[0].name;
	            			$scope.orgSelectedNameHide = false;
	            		},
	                	function(error){
	                		console.log(error);
	                		$scope.orgSelectedNameHide = true;
	                	}
	                );
	            }else{
	            	$scope.orgSelectedNameHide = true;
	            }
    			organisationId = node.org;
    		}
        	
        };

        $scope.$on("hideTypeAheadTree", function(event){
    		$scope.isEnhead = $scope.isOverEnhead = false; 
    	});


		hotkeys.add({
			combo: sysService.shortcuts.popupSubmit.key,
			description: sysService.shortcuts.popupSubmit.title,
			callback: function() {
				if($scope.isApplyBtnDisabled()) $scope.orgMoveConfirm();
			}
		});
		
		hotkeys.add({
			combo: sysService.shortcuts.popupClose.key,
			description: sysService.shortcuts.popupClose.title,
			callback: function() {
				if($scope.$parent.orgMoveModalOpen){ $scope.$parent.orgMoveModal('close'); }
			}
		});
	}]);