'use strict';
/* Employee controllers */ 

angular.module('moApp.controllers')
	.controller('organisationNew',['$scope', "$filter", "$rootScope", '$http', 'sysService', '$q', 'orgFactory', 'hotkeys', function($scope, $filter, $rootScope, $http, sysService, $q, orgFactory, hotkeys){
		$scope.org_unit;
		$scope.orgUnitName;
		$scope.orgStartDate;
		$scope.orgEndDate;
		$scope.orgUnitType;
		$scope.sysService = sysService;

		var _section = "organization";
		$scope.createSection = true;
		$scope.mainValidationError = false;
		$scope.mainValidationErrorMsg = {};

		$scope.workFlowNewOrgFlag = {
			fail : false,
			failMessage : {}
		}

		$scope.orgSections = { 
           "contact-channel":{"key": "contact-channel", "name": "Kontakt", "visible":false, data: []},
        };

		$scope.open = function($event, datePicker) {
			$event.preventDefault();
			$event.stopPropagation();
			$scope[datePicker] = ($scope[datePicker])?false:true;
		};

		$scope.dateSelect = function(dateField){
			var date = $scope[dateField];
			if(sysService.dateFormat.validateInput(date)){
				if(dateField == "orgStartDate"){
					$scope.orgStartDateTree = $filter('date')(date, 'dd-MM-yyyy');
				}
				$scope[dateField] = date;
			}
		}
		$scope.validationPassed = false;
		$scope.createNewOrgUnit = function() {
			var errorMessage = {};
			$scope.mainValidationErrorMsg = {"error": false, "section": _section, "response": ""};
			errorMessage = {};
			$scope.orgNewFail = false;

			var formObj = this.newOrgForm;
			var contactForm = this.contactChannelForm;
			var errors;
			if(formObj.$error.required){
				errors = formObj.$error.required;
			}else{
				errors = [];
			}
			for(var i = 0; i<contactForm.$error.required.length; i++){
				if(contactForm.$error.required[i].$name === 'type'){
					errors.push(contactForm.$error.required[i]);	
				}
				
			}
			if(errors.length > 0){ // Validation fail
				$scope.mainValidationError = true;
				if(!angular.isDefined($scope.org_unit) || $scope.org_unit == ""){ errorMessage['org-unit'] = {"message": $rootScope.i18n[_section+"_error_validation_required_org-unit"]}; }
				angular.forEach(errors, function(value, key) {
					errorMessage[value.$name] = {"message": $rootScope.i18n[_section+"_error_validation_required_"+value.$name]};
				}, errorMessage);
				$scope.mainValidationErrorMsg = {"error": true, "section": _section, "response": errorMessage};
			} else { // Validation pass
				// create new org unit object
				$scope.validationPassed = true;
				var newOrgUnit = {};
				newOrgUnit['user-key'] = "NULL";
				newOrgUnit['name'] = $scope.orgUnitName;
				newOrgUnit['valid-from'] = $filter('date')($scope.orgStartDate, 'dd-MM-yyyy');
				newOrgUnit['valid-to'] = $filter('date')($scope.orgEndDate, 'dd-MM-yyyy');
				newOrgUnit['org'] = $scope.org_unit.org;
				newOrgUnit['parent'] = $scope.org_unit.uuid;
				newOrgUnit['type'] = $scope.orgUnitType;

				newOrgUnit['locations'] = [
					{
						'name': $scope.orgObj.name,
						'primaer': true,
						'location': $scope.orgObj.location,
						'contact-channels': $scope.orgSections['contact-channel'].data
					}
				];

				var url = sysService.path + "o/" + $scope.org_unit.org + "/org-unit";
				$http.post(url, newOrgUnit)
				.success(function(data, status, headers, config) {
					$scope.$emit('reloadTree', true);
					sysService.recordEvent.set('success', sysService.i18n('organisation_created_successfully'));
					$scope.$parent.orgNewModal('close');
				})
				.error(function(data, status, headers, config) {
					$scope.workFlowNewOrgFlag.fail = true;
					$scope.workFlowNewOrgFlag.failMessage = data.errors;
				});
			}			

		};
		$scope.geoLocal = 1;
		// Address search autocomplete ////////////////////////////////
		$scope.getAddressList = function(val) {
			var canceler = $q.defer();
			//canceler.resolve();
			return $http.get('addressws/geographical-location', 
				{ params: { vejnavn: val, local: $scope.geoLocal},
				timeout: canceler.promise }
			).then(function(response){
				var resData = response.data;
				if($scope.geoLocal == 1){
				}else{
					angular.forEach(resData, function(value, key){
						value.vejnavn = value.vejnavn+", "+value.postdistrikt+", "+value.postnr;
					})
				}
		      	return resData;
		    });
	  	};	

		// Org Unit Types /////////////////////////////////////////////////////////////////////////////////////////////////////////
		$scope.orgUnitTypes;
		$http.get(sysService.path + 'org-unit/type').success(function(response) {
			response = _.without(response, _.findWhere(response, {name: 'Udvalg'}));
			$scope.orgUnitTypes = response;
		});

		// Location /////////////////////////////////////////////////////////////////////////////////////////////////////////
		$scope.assocAddress = [];
		$scope.loadAssoAddress = function(uuid){
			$scope.assocAddress = [];
				orgFactory.orgLocations(uuid).then(function(response) {
					var location = response;
					angular.forEach(location, function(value, index){
						$http.get('lokation/'+value.uuid).then(function(res) {
						$scope.assocAddress.push(res.data);
					});
				})
			});
		}

		// Contact /////////////////////////////////////////////////////////////////////////////////////////////////////////
		$scope.contactTypes;
		$http.get(sysService.path + 'role-types/contact/facets/type/classes/?facetKey=Contact_channel_location').success(function(response) {
			$scope.contactTypes = response;
			$scope.$broadcast('contactAvailable','contact-channel');	
		});

		$scope.$on('contactAvailable',function(event,section){
			$scope.contactChanneldropDown(section);
		});

		// Contact Channel Visibility /////////////////////////////////////////////////////////////////////////////////////////////////////////
		$scope.contactVisibilityOptions;
		$http.get(sysService.path + 'role-types/contact/facets/properties/classes/').success(function(response) {
			$scope.contactVisibilityOptions = response;
		});
		$scope.contactChanneldropDown = function(section){
			if(!$scope.contactTypes){
				return false;
			}
			$scope.type = (!$scope.orgSections[section].data.length)?$scope.contactTypes[8]:'';
		};

		// Adding contact channel /////
		$scope.addSection = function(section, obj){
			var errorMessage = {};
			var formObj = this.contactChannelForm;

			if(formObj.$error.required.length > 0){ // Validation fail
				$scope.mainValidationError = true;
				var errors = formObj.$error.required;
				angular.forEach(errors, function(value, key) {
					errorMessage[value.$name] = {"message": $rootScope.i18n[_section+"_error_validation_required_"+value.$name]};
				}, errorMessage);
				$scope.validationErrorMsg = {"error": true, "section": _section, "response": errorMessage};
			}else if(angular.isDefined(obj.type) && obj.type.name == "Telefonnummer" && angular.isDefined(obj.channel.contact_info) && obj.channel.contact_info.length != 8){
				$scope.mainValidationError = true;
				errorMessage['contact-info'] = {"message": $rootScope.i18n[_section+"_error_validation_min-length_contact-info-Telefonnummer"]};
				$scope.validationErrorMsg = {"error": true, "section": _section, "response": errorMessage};
			}else if(angular.isDefined(obj.type) && obj.type.name == "EAN-nummer" && angular.isDefined(obj.channel.contact_info) && obj.channel.contact_info.length != 13){
				$scope.mainValidationError = true;
				errorMessage['contact-info'] = {"message": $rootScope.i18n[_section+"_error_validation_min-length_contact-info-EAN-nummer"]};
				$scope.validationErrorMsg = {"error": true, "section": _section, "response": errorMessage};
			}else if(angular.isDefined(obj.type) && obj.type.name == "Faxnummer" && angular.isDefined(obj.channel.contact_info) && obj.channel.contact_info.length != 8){
				$scope.mainValidationError = true;
				errorMessage['contact-info'] = {"message": $rootScope.i18n[_section+"_error_validation_min-length_contact-info-Faxnummer"]};
				$scope.validationErrorMsg = {"error": true, "section": _section, "response": errorMessage};
			}else if(angular.isDefined(obj.type) && obj.type.name == "Afd. Webadresse" && angular.isDefined(obj.channel.contact_info) && !(/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/.test(obj.channel.contact_info)) ){
				$scope.mainValidationError = true;
				errorMessage['contact-info'] = {"message": $rootScope.i18n[_section+"_error_validation_min-length_contact-info-Afd-Webadresse"]};
				$scope.validationErrorMsg = {"error": true, "section": _section, "response": errorMessage};
			}else if(angular.isDefined(obj.type) && obj.type.name == "P-nummer" && angular.isDefined(obj.channel.contact_info) && (isNaN(obj.channel.contact_info) || obj.channel.contact_info.length != 10)){
				$scope.validationError = true;
				errorMessage['contact-info'] = {"message": $rootScope.i18n["organization_error_validation_number_contact-info-p-nummer"]};
				$scope.validationErrorMsg = {"error": true, "section": _section, "response": errorMessage};
			}else { // Validation pass
				var prom = [];
				var contactChannels = {};
				obj.channel.type = $scope.type;
				prom.push(angular.forEach(obj.channel, function(value, key){
					key = key.replace(/_/g, '-');
					if(value != "" && value && typeof(value) !== "undefined"){
						contactChannels[key] = value;
					}
				}));
				$q.all(prom).then(function (result) {
					$scope.orgSections[section].data.push(contactChannels)
					$scope.createSection = false;
					$scope.validationErrorMsg = {};
				});
			}
		};

		$scope.cancelForm = function(){
			$scope.createSection = false;
			$scope.validationErrorMsg = {};
		};

		$scope.contactTypeFirst = true;
		
		$scope.showForm = function(){
			if($scope.orgSections["contact-channel"].data.length < 1){ // first add
				$scope.type = $scope.contactTypes[8];
				$scope.contactTypeFirst = false;
			}else{
				$scope.type = '';
				$scope.contactTypeFirst = true;
				$scope.channel.visibility = '';
				$scope.channel.contact_info = '';
			}
			$scope.createSection = true;
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
		    		{ params: { query: val, 'effective-date': $scope.orgStartDateTree}}
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
			$scope.valueEnhead = $scope.orgSelectedName = node.name;
			$scope.selectedEnhead = node;
			$scope.org_unit = node;
        };

		hotkeys.add({
			combo: sysService.shortcuts.popupSubmit.key,
			description: sysService.shortcuts.popupSubmit.title,
			callback: function() {
				$scope.createNewOrgUnit();
			}
		});
		
		hotkeys.add({
			combo: sysService.shortcuts.popupClose.key,
			description: sysService.shortcuts.popupClose.title,
			callback: function() {
				if($scope.$parent.orgNewModalOpen){ $scope.$parent.orgNewModal('close'); }
			}
		});

	}]);