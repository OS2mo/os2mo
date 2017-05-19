'use strict';
/* Organisation controllers */

angular.module('moApp.controllers').
	  controller('moOrganisation',["$scope", "$http", "$filter", "$state", "$rootScope", "$modal", "orgFactory", "$location", "$timeout", "ngTableParams", "sysService", "$q",function($scope, $http, $filter, $state, $rootScope, $modal, orgFactory, $location, $timeout, ngTableParams, sysService, $q) {
	  }])	 
	  .controller('moOrganisationList',["$scope", "$http", "$filter", "$state", "$rootScope", "$modal", "orgFactory", "$location", "$timeout", "ngTableParams", "sysService", "$q",function($scope, $http, $filter, $state, $rootScope, $modal, orgFactory, $location, $timeout, ngTableParams, sysService, $q) {
	  	var _this = this;
	  	var searchParam = "";
		var stateParams = $state.params; 
		
		if(angular.isDefined(stateParams) && angular.isDefined(stateParams.query) && stateParams.query !== null){  $scope.queryString = stateParams.query; }
		$scope.organisationsFound;
		$scope.organisationsLoaded = false;
		if(angular.isDefined($scope.queryString)){
			$scope.organisations = new ngTableParams({
		        page: 1,    // show first page
		        count: 200,  // count per page
		        limit:10,	// Limit per page
		        start: 0	// Start from
		    }, {
		        total: 0,           // length of data
		        getData: function($defer, params) {
		        	var customParam = {
		        		"limit": params.count(),
		        		"start": (params.page()-1)*params.$params.limit,
		        		"query": $scope.queryString
		        	};
		        	orgFactory.organisationList(customParam).then(
	            		function(response){ 
	            			$scope.organisationsFound = true;
	            			$scope.organisationsLoaded = true;
	            			$timeout(function() {
	            				params.total(40);
	            				$defer.resolve(response);
	            			},500);
	            		},
	                	function(error){
	                		$scope.organisationsFound = false; 
	                		$scope.organisationsLoaded = true;
	                		return $q.reject(error); }
	                );
		        }
		    });
		}
	  }])
	  .controller('moOrganisationMaster',["$scope", "$http", "$filter", "$state", "$modal", 'empFactory', "$q", "$location", "sysService", "hotkeys", "$timeout", "orgFactory", function($scope, $http, $filter, $state, $modal, empFactory, $q, $location, sysService, hotkeys, $timeout, orgFactory) {
	  	$scope.sysService = sysService;
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
	  		dataAdded: false,
	  		dataUnsaved: false
	  	};
	  	$scope.orgUUID;
	  	$scope.visibleEngagementCount = 0;
	  	$scope.loadedEngagementsCount = 0;
	  	$scope.validity = ['present', 'past', 'future'];
		$scope.engagements = {
			"org-unit":{ "key": "org-unit", "visible":false}, // Editable
			"location":{"key": "location", "visible":false}, // Editable
			"contact-channel":{"key": "contact-channel", "visible":false}, // Editable
			"leader":{"key": "leader", "visible":false, "restricted": true}, // Non editable
			"engagement":{"key": "engagement", "visible":false, "restricted": true}, // Non editable
			"association":{"key": "association", "visible":false, "restricted": true}, // Non editable
			"job-function":{"key": "job-function", "visible":false, "restricted": true} // Non editable
        };
        var active = false;
        ////////////////////////////////////////////////////////////////////////////////////

		$scope.orgNewModalOpen = false;
		$scope.orgNewModal = function (state){
			if(state == "open"){
				$scope.orgNewModalOpen = true;
				$scope.orgNewInstance = $modal.open({
				  templateUrl: sysService.path+'partials/organisation/organisationNew.html',
				  controller: 'organisationNew',
				  scope : $scope,
				  backdrop: 'static',
				  keyboard: false,
				  windowClass: 'organisationNew'
				});
			}else if(state == "close"){
				$scope.orgNewModalOpen = false;
				$scope.orgNewInstance.dismiss('cancel');
			}
		};

		$scope.orgRenameModalOpen = false;
		$scope.orgRenameModal = function (state){
			if(state == "open"){
				$scope.orgRenameModalOpen = true;
				$scope.orgRenameInstance = $modal.open({
				  templateUrl: sysService.path+'partials/organisation/organisationRename.html',
				  controller: 'organisationRename',
				  scope : $scope,
				  backdrop: 'static',
				  keyboard: false,
				  windowClass: 'organisationRename'
				});
			}else if(state == "close"){
				$scope.orgRenameModalOpen = false;
				$scope.orgRenameInstance.dismiss('cancel');
			}
		};

		$scope.orgEndModalOpen = false;
		$scope.orgEndModal = function (state){
			if(state === "open"){
				$scope.orgEndModalOpen = true;
				$scope.orgEndInstance = $modal.open({
					templateUrl: sysService.path+'partials/organisation/organisationEnd.html',
					controller: 'organisationEnd',
					scope : $scope,
					backdrop: 'static',
					keyboard: false,
					windowClass: 'organisationEnd'
				});
			}else if(state === "close"){
				$scope.orgEndModalOpen = false;
				$scope.orgEndInstance.dismiss('cancel');
			}
		};


		$scope.orgAssocModalOpen = false;
		$scope.orgAssocModal = function (state){
			if(state == "open"){
				$scope.orgAssocModalOpen = true;
				$scope.orgAssocInstance = $modal.open({
					templateUrl: sysService.path+'partials/organisation/organisationAssociation.html',
					controller: 'organisationAssoc',
					scope : $scope,
					backdrop: 'static',
					keyboard: false,
					windowClass: 'organisationAssoc'
				});
			}else if(state == "close"){
				$scope.orgAssocModalOpen = false;
				$scope.orgAssocInstance.dismiss('cancel');
			}
		};

		$scope.orgMoveModalOpen = false;
		$scope.orgMoveModal = function (state){
			if(state == "open"){
				$scope.orgMoveModalOpen = true;
				$scope.orgMoveInstance = $modal.open({
				  templateUrl: sysService.path+'partials/organisation/organisationMove.html',
				  controller: 'organisationMove',
				  scope : $scope,
				  backdrop: 'static',
				  keyboard: false,
				  windowClass: 'organisationMove'
				});
			}else if(state == "close"){
				$scope.orgMoveModalOpen = false;
				$scope.orgMoveInstance.dismiss('cancel');
			}
		};

		$scope.orgViewOpen = false;
		$scope.orgView = function (state, uuid, date){
			if(state == "open"){
				if(angular.isDefined(uuid) && uuid != ""){ 
					$scope.flag.orgFound = false;
	  				$scope.flag.orgInfoLoaded = false;
	  				$scope.flag.orgEngagementsFound = false;
	  				$scope.organisation = {};
					$scope.cleanUpOrgData();
				}
				$scope.orgViewInstance = $modal.open({
				  templateUrl: sysService.path+'partials/organisation/organisationViewEdit.html',
				  controller: 'moOrganisationViewEdit',
				  scope : $scope,
				  backdrop: 'static',
				  keyboard: false,
				  windowClass: 'organisationViewEdit'
				});
				$scope.orgViewInstance.opened.then(function() {
					$timeout(function(){
						$scope.orgViewOpen = true;
						$scope.flag.orgEdit = false;
						$scope.flag.orgCreate = false;
						if(angular.isDefined(uuid) && uuid != ""){
							orgFactory.orgHeaders().then(function(response) {
								$scope.cleanUpOrgData();
								$scope.tables = response;
								$scope.initOrgData(uuid, date);
							});
						}
					}, 2000); 
				});
			}else if(state == "close"){
				$scope.orgViewOpen = false;
				$scope.flag.orgEdit = false;
				$scope.flag.orgCreate = false;
				if(angular.isDefined($scope.orgViewInstance))
					$scope.orgViewInstance.dismiss('cancel');
				if(angular.isDefined($scope.orgEditInstance))
					$scope.orgEditInstance.dismiss('cancel');
			}
		};

		$scope.orgEditOpen = false;
		$scope.orgEdit = function (state, uuid, date){
			if(state == "open"){
				if(angular.isDefined(uuid) && uuid != ""){ 
					$scope.flag.orgFound = false;
	  				$scope.flag.orgInfoLoaded = false;
					$scope.flag.orgEngagementsFound = false;
	  				$scope.organisation = {};
					$scope.cleanUpOrgData();
				}
				$scope.orgEditInstance = $modal.open({
				  templateUrl: sysService.path+'partials/organisation/organisationViewEdit.html',
				  controller: 'moOrganisationViewEdit',
				  scope : $scope,
				  backdrop: 'static',
				  keyboard: false,
				  windowClass: 'organisationViewEdit'
				});
				$scope.orgEditInstance.opened.then(function() {
					$timeout(function(){
						$scope.orgEditOpen = true;
						$scope.flag.orgEdit = true;
						$scope.flag.orgCreate = true;
						if(angular.isDefined(uuid) && uuid != ""){
							orgFactory.orgHeaders().then(function(response) {
								$scope.cleanUpOrgData();
								$scope.tables = response;
								$scope.initOrgData(uuid, date);
							});
						}
					}, 2000); 
				});
			}else if(state == "close"){
				$scope.orgEditOpen = false;
				$scope.flag.orgEdit = false;
				$scope.flag.orgCreate = false;
				if($scope.flag.dataUnsaved){
					if(sysService.state.data.page.key == "organisation" && sysService.state.data.page.subKey == "detail"){
						$scope.initOrgData();
					}
					$scope.flag.dataUnsaved=false;
				}
				if(angular.isDefined($scope.orgViewInstance))
					$scope.orgViewInstance.dismiss('cancel');
				if(angular.isDefined($scope.orgEditInstance))
					$scope.orgEditInstance.dismiss('cancel');
			}
		};
		////////////////////////////////////////////////////////////////////////////////
		$scope.initOrgData = function (uuid, date){
			uuid = (angular.isDefined(uuid))?uuid:$scope.orgUUID;
			date = '';//(angular.isDefined(date))?date:$scope.orgEffectiveDate;
			$scope.cleanUpOrgData();
			$scope.contactChannelHasTelNo = false;
			$scope.visibleEngagementCount = 0;
	  		$scope.loadedEngagementsCount = 0;
	  		$scope.allEngagementsLoaded = false;
			sysService.enableToolbar = false;
			
   			orgFactory.orgInfos(uuid, date).then(function(response){
				response = response[0];
				$scope.organisation = response;
				$scope.orgUUID = response["uuid"]; 
				$scope.visibleEngagementsCount = 0;
				$scope.flag.orgFound = true;
				$scope.flag.orgInfoLoaded = true;
				active = false;
				angular.forEach($scope.engagements, function(role, key){
					if(response.activeName == "Odense Kommune"){
						if(!angular.isDefined(role.restricted)){
							$scope.loadEngagements(uuid, key, date);
						}
					}else{
						$scope.loadEngagements(uuid, key, date);
					}
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

		// Hotkeys for workflow actions
		hotkeys.add({
			combo: sysService.shortcuts.organisationWorkflowEnd.key,
			description: sysService.shortcuts.organisationWorkflowEnd.title,
			callback: function() {
				if(!$scope.orgEndModalOpen && (sysService.setupACL.validate('o|write'))){
					$scope.orgEndModal('open');
				}
			}
		});

		hotkeys.add({
			combo: sysService.shortcuts.organisationWorkflowRename.key,
			description: sysService.shortcuts.organisationWorkflowRename.title,
			callback: function() {
				if(!$scope.orgRenameModalOpen && (sysService.setupACL.validate('o|write'))){
					$scope.orgRenameModal('open');
				}
			}
		});

		hotkeys.add({
			combo: sysService.shortcuts.organisationWorkflowNew.key,
			description: sysService.shortcuts.organisationWorkflowNew.title,
			callback: function() {
				if(!$scope.orgNewModalOpen && (sysService.setupACL.validate('o|write'))){
					$scope.orgNewModal('open');
				}
			}
		});

		hotkeys.add({
			combo: sysService.shortcuts.organisationWorkflowMove.key,
			description: sysService.shortcuts.organisationWorkflowMove.title,
			callback: function() {
				if(!$scope.orgMoveModalOpen && (sysService.setupACL.validate('o|write'))){
					$scope.orgMoveModal('open');
				}
			}
		});

		var activeEngagement = false;
		$scope.contactChannelHasTelNo = false;
		$scope.loadEngagements = function(uuid, engagement, date){
			var prom = [];
			var table = $scope.tables[engagement];
			var defaultTab = '';
			var visible = false;
			
			$scope.engagements[engagement]['visible'] = visible;

			$scope.engagements[engagement].errorCreate = false;
			$scope.engagements[engagement].errorUpdate = false;
			$scope.engagements[engagement].changed = false;
			$scope.engagements[engagement].added = false;

			angular.forEach($scope.validity, function(validity, position){
				table.tr[validity] = [];
				$scope.engagements[engagement][validity] = false; 
				prom.push(orgFactory.orgRoles(uuid, engagement, '', validity).then(function(response){
					table.tr[validity] = [];
					table.tr[validity] = response;
					if(response.length > 0){
						$scope.engagements[engagement].timeStamp = _.now();
						// Set default tab
						if(engagement == 'contact-channel'){
							angular.forEach(response, function(value, key){
								if(value.type['user-key'] == 'Telephone_number'){
									$scope.contactChannelHasTelNo = true;
									sysService.enableToolbar = true;
								}
							});
						}
						if(engagement == 'org-unit'){ $scope.engagements[engagement].active = true;}
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
							role.defaultTab = 'present';//validity;
							defaultTabSet = true;
							$scope.flag.orgEngagementsFound = true;
						}
					});
					//$scope.visibleEngagementsCount++;
					$scope.engagements[engagement]['visible'] = true;
					$scope.visibleEngagementsCount++;
				}
				$scope.loadedEngagementsCount++;
			});
		};

		$scope.$watch('loadedEngagementsCount', function(newVal){
			if(_.size($scope.engagements) == newVal){
				$scope.allEngagementsLoaded = true;
				if(!$scope.contactChannelHasTelNo){
					console.log('Disable toolbar');
					sysService.enableToolbar = false;
				}else{
					console.log('Enable toolbar');
					sysService.enableToolbar = true;
				}
			}
		})
	  }])
	.controller('moOrganisationDetail',["$scope", "$http", "$filter", "$state", "$rootScope", "$modal", 'orgFactory', "$q", "$location", "sysService", "hotkeys", function($scope, $http, $filter, $state, $rootScope, $modal, orgFactory, $q, $location, sysService, hotkeys) {
			$scope.sysService = sysService;
			$scope.$watch('timeMachine', function(newVal){
				if(angular.isDefined(newVal) && newVal.cpr != ""){
					_loadOrgDetails(newVal.cpr, newVal.date);
				}
			})

			var _loadOrgDetails = function(cpr, date){
				$scope.$parent.orgInfoLoaded = false;
		        orgFactory.orgHeaders().then(function(response) {
					$scope.$parent.cleanUpOrgData();
					$scope.$parent.tables = response;
					$scope.$parent.initOrgData(cpr, date);
				});
			}

			/////////////////////////////////////////////////////////////////
			var stateParams = $state.params;
			if(stateParams && stateParams.cpr){ // If URL have UUID/User-Key
				_loadOrgDetails(stateParams.cpr, stateParams.date);

				hotkeys.add({
					combo: sysService.shortcuts.organisationView.key,
					description: sysService.shortcuts.organisationView.title,
					callback: function() {
						if(!$scope.$parent.orgViewOpen){
							$scope.$parent.orgView('open');
						}
					}
				});

				hotkeys.add({
					combo: sysService.shortcuts.organisationEdit.key,
					description: sysService.shortcuts.organisationEdit.title,
					callback: function() {
						if(!$scope.$parent.orgEditOpen && (sysService.setupACL.validate('o|write'))){
							$scope.$parent.orgEdit('open');
						}
					}
				});


				$scope.$parent.$watch("visibleEngagementsCount", function(newVal){
					if(newVal > 0){
						angular.forEach($scope.$parent.engagements, function(value, index){
							if(value.visible){
								hotkeys.add({
									combo: "alt+"+newVal,
									description: 'Switch tab',
									callback: function() {
										$scope.$parent.engagements[index].active = true
									}
								});
							}
						})
					}
				});
			}
	}])	  
	.controller('moOrganisationViewEdit',["$scope", "$http", "$filter", "$state", "$rootScope", "$modal", "sysService", "orgFactory", "$q", "hotkeys", "$timeout",function($scope, $http, $filter, $state, $rootScope, $modal, sysService, orgFactory, $q, hotkeys, $timeout) {
		$scope.sysService = sysService;
		$scope.$on('resetViewEdit', function(event, data){
			$scope.editOrganisationFunc.resetViewEdit();
		});
		$scope.sysService = sysService;
		$scope.inlineDatePicker = {'from': false, 'to': false};
		$scope.openInlineDatePicker = function($event, cal) {
			$event.preventDefault();
			$event.stopPropagation();
			angular.forEach($scope.inlineDatePicker, function(value, key){
				if(key != cal){ $scope.inlineDatePicker[key] = false; }
			});
			$scope.inlineDatePicker[cal] = ($scope.inlineDatePicker[cal])?false:true;
		};
		$scope.closeInlineDatePicker = function() {
			angular.forEach($scope.inlineDatePicker, function(value, key){
				$scope.inlineDatePicker[key] = false;
			});
		};

		$scope.openUpdateLocationEdit = function (field, type, index, period) {
			var modalInstance = $modal.open({
				templateUrl: sysService.path+'partials/organisation/modalOrganisationLocationUpdate.html',
				controller: ModalInstanceCtrlEdit,
				windowClass: 'organisationLocationUpdate'
			});

			modalInstance.result.then(function (flag) {
				var row = $scope.$parent.tables[type]['tr'][period][index];
				if(flag =='yes'){
					row.primaer = field = !field;
				}else{
					row.primaer = field;
				}
				console.log("Field set to", row, row.primaer);	
			}, function () {
			});
		};

		var ModalInstanceCtrlEdit = function ($scope, $modalInstance) {
			$scope.ok = function (msg) {
				$modalInstance.close(msg);
			};
			$scope.cancel = function () {
				$modalInstance.close('no');
				$modalInstance.dismiss('cancel');
			};
		};

		$scope.geoLocalEdit = 1;
		$scope.editOrganisationFunc = {
			updatedData : {
				"org-unit":{},
				"location":{},
				"contact-channel":{},
				"leader":{},
				"engagement":{},
				"association":{},
				"job-function":{}
        	},
        	opened : false,
        	datePicker: function(state){
        		if(state == "open"){
        			$scope.editOrganisationFunc.opened = true;
        		}else{
        			$scope.editOrganisationFunc.opened = false;
        		}
        	},
        	resetViewEdit: function(){
        		angular.forEach($scope.orgEditanisationFunc.updatedData, function(value, index){
					value = {};
				});
        	},
        	setGeoLocal : function(val){
        		$scope.geoLocalEdit = val.geoLocalEdit;
			},
			validationError : [],
			formatDate : function(strVal) {
    			strVal = $filter('date')(strVal, 'dd-MM-yyyy');
    		    return strVal;
		  	},
        	loacationAddress : function(val){
				var canceler = $q.defer();
				//canceler.resolve();
				return $http.get('addressws/geographical-location',
                                 {
                                     params: {
                                         vejnavn: val,
                                         local: ($scope.geoLocalEdit &&
                                                 $scope.$parent.organisation.org)
                                     },
				                     timeout: canceler.promise
                                 }
				).then(function(response){
					var resData = response.data;
					if($scope.geoLocalEdit == 1){
					}else{
						angular.forEach(resData, function(value, key){
							value.vejnavn = value.vejnavn+", "+value.postdistrikt+", "+value.postnr;
						})
					}
			      	return resData;
			    });
        	},
			orgTypes: {},
        	orgType : function(str, role) {
				var _this = this;
				if(!angular.isDefined(role)){
	    			return _this.orgTypes.length ? null : $http.get('org-unit/type').success(function(response) {
	      				response = _.without(response, _.findWhere(response, {name: 'Udvalg'}));
						_this.orgTypes = response;
	    			});
    			}else{
					if(angular.isDefined(str) && _this.orgTypes && _this.orgTypes.length) {
						var selected = $filter('filter')(_this.orgTypes, {uuid: str.uuid});
						return selected.length ? selected[0].name : '---'; /* Not set */
					} else {
						if(angular.isDefined(str)){
							return str.name || '---'; /* Not set */
						}else{
							return '---'; /* Not set */
						}
					}
    			}
  			},
  			kontactTypes: {},
			kontactType : function(str, role) {
				var _this = this;
				if(!angular.isDefined(role)){
	    			return _this.kontactTypes.length ? null : $http.get('role-types/contact/facets/type/classes/?facetKey=Contact_channel_location').success(function(response) {
	      				_this.kontactTypes = response;
	    			});
    			}else{
					if(angular.isDefined(str) && _this.kontactTypes && _this.kontactTypes.length) {
						var selected = $filter('filter')(_this.kontactTypes, {uuid: str.uuid});
						return selected.length ? selected[0].name : '---'; /* Not set */
					} else {
						if(angular.isDefined(str)){
							return str.name || '---'; /* Not set */
						}else{
							return '---'; /* Not set */
						}
					}
    			}
  			},
  			visibilities: {},
			visibility : function(str, role) {
				var _this = this;
				if(!angular.isDefined(role)){
	    			return _this.visibilities.length ? null : $http.get('role-types/contact/facets/properties/classes/').success(function(response) {
	      				_this.visibilities = response;
	    			});
    			}else{
					if(angular.isDefined(str) && _this.visibilities && _this.visibilities.length) {
						var selected = $filter('filter')(_this.visibilities, {uuid: str.uuid});
						return selected.length ? selected[0].name : '---'; /* Not set */
					} else {
						if(angular.isDefined(str)){
							return str.name || '---'; /* Not set */
						}else{
							return '---'; /* Not set */
						}
					}
    			}
  			},

  			locations: {},
			location : function(dataRow, role, flag) {
				var _this = this;
				var date = (dataRow['valid-from'])?$filter('date')(dataRow['valid-from'], "dd-MM-yyyy"):'';
				if(!flag){
	    			return orgFactory.orgRoles($scope.$parent.orgUUID, 'location', date, '', true).then(function(response){
	      				_this.locations = response;
	    			});
    			}else{
					if(angular.isDefined(dataRow['location']) && _this.locations && _this.locations.length) {
						var selected = $filter('filter')(_this.locations, {uuid: dataRow['location'].uuid});
						return selected.length ? selected[0].name : '---'; /* Not set */
					} else {
						if(angular.isDefined(dataRow['location'])){
							return dataRow['location'].name || '---'; /* Not set */
						}else{
							return '---'; /* Not set */
						}
					}
    			}
  			},
  			updRowBeforeSave: function(row, field, _this){
  				if(field == "valid-from" || field == "valid-to"){
  					row[field+'-updated'] = _this;
  					if(field == "valid-from" && (!angular.isDefined(_this) || _this == "" || !sysService.dateFormat.validateInput(_this))){
  						return $rootScope.i18n["enter_valid-from_date"];
  					}

  					if(field == "valid-to" && !sysService.dateFormat.validateInput(_this) && _this != "" && _this !== null){
  						return $rootScope.i18n["enter_valid-to_date"];
  					}

  					var validFrom = row['valid-from'];
  					if(angular.isDefined(row['valid-from-updated']) && row['valid-from-updated'] != ''){
						validFrom = row['valid-from-updated'];
					}

					var validTo = row['valid-to'];
  					if(angular.isDefined(row['valid-to-updated']) && row['valid-to-updated'] != ''){
						validTo = row['valid-to-updated'];
					}

					validFrom = $filter('date')(validFrom, "dd-MM-yyyy");
					validTo = (validTo == "" || validTo === null)?"":$filter('date')(validTo, "dd-MM-yyyy");

					// Validation
					validFrom=validFrom.split("-");
					validFrom=validFrom[1]+"/"+validFrom[0]+"/"+validFrom[2];

					if(validTo != ""){
						validTo=validTo.split("-");
						validTo=validTo[1]+"/"+validTo[0]+"/"+validTo[2];					
					}

					if(validTo != ""){
						if (new Date(validTo).getTime() < new Date(validFrom).getTime()) {
						    return $rootScope.i18n["enter_valid_date_range"];
						}
					}
				}else if(field == 'primaer' && !_this.dataRow.primaer){
  					var modalInstance = $modal.open({
						templateUrl: sysService.path+'partials/organisation/modalOrganisationLocationUpdate.html',
						controller: ModalInstanceCtrlEdit,
						windowClass: 'organisationLocationUpdate'
					});

					modalInstance.result.then(function (flag) {
						if(flag =='yes'){
							_this.dataRow.primaer = (_this.dataRow.primaer)?true:false;
						}else{
							_this.dataRow.primaer = false;
						}
					}, function () {
					});	
				}else if(field == "type"){
					var _editOrganisationFuncObj = this;
	    			var selected = $filter('filter')(_editOrganisationFuncObj.kontactTypes, {uuid: _this});
					row['type-updated'] = selected.length ? selected[0].name : '';
				}else if(field == "contact-info"){
					var errorMessage = '';
					var rowType = row.type.name;
					if(angular.isDefined(row['type-updated']) && row['type-updated'] != ''){
						rowType = row['type-updated'];
					}
					if(!angular.isDefined(_this) && _this.length == 0){
						errorMessage = $rootScope.i18n["organization_error_validation_required_contact-info"];
						return errorMessage;
					}else if(rowType == "Telefonnummer" && _this.length != 8){
						errorMessage = $rootScope.i18n["organization_error_validation_min-length_contact-info-Telefonnummer"];
						return errorMessage;
					}else if(rowType == "EAN-nummer" && _this.length != 13){
						errorMessage = $rootScope.i18n["organization_error_validation_min-length_contact-info-EAN-nummer"];
						return errorMessage;
					}else if(rowType == "Faxnummer" && _this.length != 8){
						errorMessage = $rootScope.i18n["organization_error_validation_min-length_contact-info-Faxnummer"];
						return errorMessage;
					}else if(rowType == "Afd. Webadresse" && !(/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/.test(_this)) ){
						errorMessage = $rootScope.i18n["organization_error_validation_min-length_contact-info-Afd-Webadresse"];
						return errorMessage;
					}else if(rowType == "P-nummer" && (isNaN(_this)|| _this.length != 10)){
						errorMessage = $rootScope.i18n["organization_error_validation_number_contact-info-p-nummer"];
						return errorMessage;
					}
				}else if(field == "valid-from"){
					if(!angular.isDefined(_this) || _this == null){
						errorMessage = $rootScope.i18n["valid-from-required"];
						return errorMessage;
					}
  				}else{
  					if(angular.isDefined(row[field])){ return; }else{ return row[field] = {}; }
  				}
  			},
			updRow : function(type, index, period, data){
  				var row = $scope.$parent.tables[type]['tr'][period][index];
				$scope.$parent.flag.dataUnsaved = true;
				if(angular.isDefined(row.uuid)){
					$scope.$parent.engagements[type].changed = true;
					row.changed = true;
	  				$scope.$parent.flag.dataUpdated = true;
  				}
  			},
			saveRows : function(){
				var _this = this;
  				// Reset validation
				angular.forEach(this.validationError, function(value, key){
					_this.validationError[value] = "";
				});
  				if($scope.$parent.flag.dataUpdated){
					$scope.$parent.flag.orgEditSuccess = false;

					var editPromise = [];
					var createPromise = [];
					angular.forEach($scope.$parent.engagements, function(role, key){
						var postObj = $scope.$parent.tables[key]['tr'];
						role.errorCreate = false; role.errorUpdate = false;
						angular.forEach(postObj, function(value, k){
							angular.forEach(value, function(data, dataKey){
								if(!angular.isDefined(data.uuid) && angular.isDefined(role.added) && role.added){ // CREATE
									data["valid-from"] = $filter('date')(data["valid-from"], 'dd-MM-yyyy');
									data["valid-to"] = $filter('date')(data["valid-to"], 'dd-MM-yyyy');

						   			if(key == "contact-channel"){ // Contact channel create
										var postDataOld = data;
										var locationID = data['location'].uuid;
										data = data['location'];
										data['contact-channels'] = [];
										data['contact-channels'][0] = {
											'contact-info': postDataOld['contact-info'],
											'visibility': postDataOld['visibility'],
											'type': postDataOld['type'],
											'valid-to': postDataOld['valid-to'],
											'valid-from': postDataOld['valid-from']
										};
										data["person"]=$scope.$parent.orgUUID;
										data["role-type"]=key;
										data["user-key"]="NULL";

							   			createPromise.push(orgFactory.orgCreateContactChannnel($scope.$parent.orgUUID, 'location', locationID, JSON.stringify(data)).then(function(response) { // Post Success
											var data = response.data;
											if(response.status == 200 || response.status == 201){ // Post Success
											}else{ // Post Error
												role.errorCreate = true;
												role.errorCreateMessage = (data["errors"])?data["errors"]:{};
											}
										},function(error){
										}));
									}else{ // Location create
										// data["person"]=$scope.$parent.orgUUID;
										// data["role-type"]=key;
										// data["user-key"]="NULL";
							   			createPromise.push(orgFactory.orgCreate(key, $scope.$parent.orgUUID, JSON.stringify(data)).then(function(response) { // Post Success
											var data = response.data;
											if(response.status == 200 || response.status == 201){ // Post Success
											}else{ // Post Error
												role.errorCreate = true;
												role.errorCreateMessage = (data["errors"])?data["errors"]:{};
											}
										},function(error){
										}));
									}

								}else if(angular.isDefined(data.uuid) && angular.isDefined(data.changed) && data.changed){ // UPDATE
									data["valid-from"] = $filter('date')(data["valid-from"], 'dd-MM-yyyy');
									data["valid-to"] = $filter('date')(data["valid-to"], 'dd-MM-yyyy');

									editPromise.push(orgFactory.orgUpdateRole($scope.$parent.orgUUID, key, data["uuid"], JSON.stringify(data)).then(function(response) { // Post Success
										var data = response.data;
										if(response.status == 200 || response.status == 201){ // Post Success
										}else{ // Post Error
											role.errorUpdate = true;
											role.errorUpdateMessage = (data["errors"])?data["errors"]:{};
										}
									},function(error){
									}));
								}
							});
						});
					});

					$q.all(createPromise).then(function (result) {
						$q.all(editPromise).then(function (result) {
							var deferred = $q.defer();
							var prom = deferred.promise;
							var closeModal = true;
							prom.then(function () {
								angular.forEach($scope.$parent.engagements, function(role, key){
									if((angular.isDefined(role.changed) && role.changed) || (angular.isDefined(role.added) && role.added)){
										if(angular.isDefined(role.errorUpdate) && role.errorUpdate){
											closeModal = false;
											$scope.$parent.flag.dataUnsaved = true;
										}else if(angular.isDefined(role.errorCreate) && role.errorCreate){
											closeModal = false;
											$scope.$parent.flag.dataUnsaved = true;
										}else{
											$scope.$parent.flag.dataUnsaved = false;
											role.errorCreate = false;
											role.errorUpdate = false;
											role.changed = false;
											role.added = false;
											if(sysService.state.data.page.key == "organisation" && sysService.state.data.page.subKey == "detail"){
												$scope.$parent.loadEngagements($scope.$parent.orgUUID, key);
											}
										}
									}
								});
							}).then(function () {
								if(closeModal){
									sysService.recordEvent.set('success', sysService.i18n('organisation_unit_updated_successfully_label'));
									$scope.$parent.orgEdit('close');
									$scope.$parent.flag.dataUpdated = false;
								}
							});
							$timeout(function() {
								deferred.resolve();
							}, 2000);
						});
					});
  				}
  			}
		}

		hotkeys.add({
			combo: sysService.shortcuts.popupClose.key,
			description: sysService.shortcuts.popupClose.title,
			callback: function() {
				if($scope.$parent.orgViewOpen || $scope.$parent.orgEditOpen){
					if(!$scope.$parent.editOrg){ //View popup close 
						$scope.$parent.orgView('close');
					}else{ //Edit popup close
						$scope.$parent.orgEdit('close');
					}
				}
			}
		});

		hotkeys.add({
			combo: sysService.shortcuts.popupSubmit.key,
			description: sysService.shortcuts.popupSubmit.title,
			callback: function() {
				if($scope.$parent.orgEditOpen && $scope.$parent.flag.dataUpdated){
					$scope.editOrganisationFunc.saveRows();
				}
			}
		});
	}]);
	


angular.module('moApp.controllers').
	controller('organisationCreateEngagement',["$scope", 'orgFactory', "$filter", "$rootScope", "sysService", "$http", "$q", "$modal", function($scope, orgFactory, $filter, $rootScope, sysService, $http, $q, $modal) {
		var errorMessage = {};
		$scope.cleanUp = function(){
			$scope.createEngagement = false;
			$scope.dataAdding = false;
			$scope.validationError = false;
			$scope.orgObj = {}; 
			$scope.validationErrorMsg = {};
			errorMessage = {};
		};
		$scope.cleanUp();
		$scope.cancelForm = function(){
			$scope.cleanUp();
		};

		$scope.openUpdateLocationCreate = function () {
			var modalInstance = $modal.open({
				templateUrl: sysService.path+'partials/organisation/modalOrganisationLocationUpdate.html',
				controller: ModalInstanceCtrlCreate,
				windowClass: 'organisationLocationUpdate'
			});

			modalInstance.result.then(function (flag) {
				$scope.orgObj.primaer = (flag == 'yes')?true:false;
			}, function () {
			});
		};

		var ModalInstanceCtrlCreate = function ($scope, $modalInstance) {
			$scope.ok = function (msg) {
				$modalInstance.close(msg);
			};
			$scope.cancel = function () {
				$modalInstance.close('no');
				$modalInstance.dismiss('cancel');
			};
		};

		$scope.geoLocal = 1;
		$scope.createOrganisationFunc = {
        	loacationAddress : function(val){
				var canceler = $q.defer();
				//canceler.resolve();
				return $http.get('addressws/geographical-location', 
                                 {
                                     params: {
                                         vejnavn: val,
                                         local: ($scope.geoLocal &&
                                                 $scope.$parent.organisation.org)
                                     },
				                     timeout: canceler.promise
                                 }
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
        	},
        	kontaktVisibilities: {},
        	kontaktVisibility : function(){
        		var _this = this;
        		return _this.kontaktVisibilities.length ? null : $http.get('role-types/contact/facets/properties/classes/', {cache: true}).success(function(response) {
	      			_this.kontaktVisibilities = response;
	    		});
        	},
        	kontaktTypes: {},
        	kontaktType : function(){
        		var _this = this;
        		return _this.kontaktTypes.length ? null : $http.get('role-types/contact/facets/type/classes/?facetKey=Contact_channel_location', {cache: true}).success(function(response) {
	      			_this.kontaktTypes = response;
	    		});
        	},
        	kontaktLocations: {},
        	locationDisabled: true,
        	kontaktLocation : function(date){
        		var _this = this;
        		if(_this.kontaktLocations.length){
        			return null;
        		}else{
        			orgFactory.orgRoles($scope.$parent.orgUUID, 'location', $filter('date')(date, "dd-MM-yyyy"),'',true).then(function(response){
        				_this.kontaktLocations = response;
        				_this.locationDisabled = false;
        				return _this.kontaktLocations;
        			})
        		}
        	},
        	updLocation : function(chk){
        		if(chk.orgObj.primaer){
					$scope.openUpdateLocationCreate();
				}
        	}
		}

		$scope.engagementCreate = function(){
			$scope.createOrganisationFunc.kontaktVisibility();			
			$scope.createOrganisationFunc.kontaktType();			
			//$scope.createOrganisationFunc.kontaktLocation();			
		}

		$scope.engagementEdit = function(date){
			$scope.editOrganisationFunc.visibility();			
			$scope.editOrganisationFunc.kontactType();			
			$scope.editOrganisationFunc.location(date);			
		}

		$scope.$watch('orgObj.valid_from', function(newVal){
			if(angular.isDefined(newVal)){
				$scope.createOrganisationFunc.locationDisabled = true;
				$scope.createOrganisationFunc.kontaktLocation(newVal)
			}

		})

		$scope.saveOrganisation = function(section, orgUUID, obj){
			$scope.validationErrorMsg = {"error": false, "section": section	, "response": ""};
			$scope.$parent.flag.orgCreateSuccess = false;
			errorMessage = {};
			// validation
			if($scope.orgCreateForm.$error.required.length > 0){ // Validation fail
				$scope.validationError = true;
				var errors = $scope.orgCreateForm.$error.required
				angular.forEach(errors, function(value, key) {
					errorMessage[value.$name] = {"message": $rootScope.i18n[section+"_error_validation_required_"+value.$name]};
				}, errorMessage);
				$scope.validationErrorMsg = {"error": true, "section": section, "response": errorMessage};
			}else if(section == "contact-channel" && angular.isDefined(obj.orgObj.type) && obj.orgObj.type.name == "Telefonnummer" && angular.isDefined(obj.orgObj.contact_info) && obj.orgObj.contact_info.length != 8){
				$scope.validationError = true;
				errorMessage['contact-info'] = {"message": $rootScope.i18n["organization_error_validation_min-length_contact-info-Telefonnummer"]};
				$scope.validationErrorMsg = {"error": true, "section": section, "response": errorMessage};
			}else if(section == "contact-channel" && angular.isDefined(obj.orgObj.type) && obj.orgObj.type.name == "EAN-nummer" && angular.isDefined(obj.orgObj.contact_info) && obj.orgObj.contact_info.length != 13){
				$scope.validationError = true;
				errorMessage['contact-info'] = {"message": $rootScope.i18n["organization_error_validation_min-length_contact-info-EAN-nummer"]};
				$scope.validationErrorMsg = {"error": true, "section": section, "response": errorMessage};
			}else if(section == "contact-channel" && angular.isDefined(obj.orgObj.type) && obj.orgObj.type.name == "Faxnummer" && angular.isDefined(obj.orgObj.contact_info) && obj.orgObj.contact_info.length != 8){
				$scope.validationError = true;
				errorMessage['contact-info'] = {"message": $rootScope.i18n["organization_error_validation_min-length_contact-info-Faxnummer"]};
				$scope.validationErrorMsg = {"error": true, "section": section, "response": errorMessage};
			}else if(section == "contact-channel" && angular.isDefined(obj.orgObj.type) && obj.orgObj.type.name == "Afd. Webadresse" && angular.isDefined(obj.orgObj.contact_info) && !(/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/.test(obj.orgObj.contact_info)) ){
				$scope.validationError = true;
				errorMessage['contact-info'] = {"message": $rootScope.i18n["organization_error_validation_min-length_contact-info-Afd-Webadresse"]};
				$scope.validationErrorMsg = {"error": true, "section": section, "response": errorMessage};
			}else if(section == "contact-channel" && angular.isDefined(obj.orgObj.type) && obj.orgObj.type.name == "P-nummer" && angular.isDefined(obj.orgObj.contact_info) && (isNaN(obj.orgObj.contact_info) || obj.orgObj.contact_info.length != 10)){
				$scope.validationError = true;
				errorMessage['contact-info'] = {"message": $rootScope.i18n["organization_error_validation_number_contact-info-p-nummer"]};
				$scope.validationErrorMsg = {"error": true, "section": section, "response": errorMessage};
			}else{ // Validation pass
				// Post data
				$scope.validationError = false;
				var postData = {};
				$scope.orgObj.valid_from = ($scope.orgObj.valid_from == "" || !angular.isDefined($scope.orgObj.valid_from))?"infinity":$filter('date')($scope.orgObj.valid_from, "dd-MM-yyyy");
				$scope.orgObj.valid_to = ($scope.orgObj.valid_to == "" || !angular.isDefined($scope.orgObj.valid_to))?"infinity":$filter('date')($scope.orgObj.valid_to, "dd-MM-yyyy");

				angular.forEach($scope.orgObj, function(value, key) {
					key = key.replace(/_/g, '-');
					if(value != "" && value && typeof(value) !== "undefined"){
						postData[key] = value;
					}else{
						//$scope.validationError = true;
					}
				}, postData);

				$scope.engagementEdit($scope.orgObj.valid_from);
				var state;
				var startDate = $scope.orgObj.valid_from;
				startDate=startDate.split("-");
				startDate=startDate[1]+"/"+startDate[0]+"/"+startDate[2];

				var endDate = $scope.orgObj.valid_to;
				if(endDate === null || endDate == "" || endDate == "infinity" || !angular.isDefined(endDate)){
					endDate = '';
				}else{
					endDate=endDate.split("-");
					endDate=endDate[1]+"/"+endDate[0]+"/"+endDate[2];					
				}

				if(endDate != ""){
					if (new Date(endDate).getTime() < new Date().getTime()) {
					    state = 'past';
					}else if (new Date(endDate).getTime() >= new Date().getTime()) {
					    state = 'present';
					}else if (new Date(startDate).getTime() > new Date().getTime()) {
						state = 'future';
					}
				}else{
					if (new Date(startDate).getTime() <= new Date().getTime()) {
					    state = 'present';
					}else if (new Date(startDate).getTime() > new Date().getTime()) {
						state = 'future';
					}
				}
				if(endDate != ""){
					if (new Date(endDate).getTime() < new Date(startDate).getTime()) {
						$scope.validationError = true;
						errorMessage[section] = {"message": $rootScope.i18n["enter_valid_date_range"]};
						$scope.validationErrorMsg = {"error": true, "section": section, "response": errorMessage};
					}
				}
				if(!$scope.validationError){
					$scope.$parent.tables[section]['tr'][state].push(postData);
					$scope.engagements[section][state] = true;
					$scope.engagements[section]['display'] = true;
					$scope.engagements[section]['defaultTab'] = 'present';
					$scope.engagements[section]['visible'] = 'present';
					$scope.engagements[section][state] = true;
					$scope.$parent.flag.dataUpdated = true;
					$scope.$parent.flag.dataUnsaved = true;
					$scope.engagements[section]['added'] = true;
					$scope.createEngagement = false;
					$scope.orgObj = null;
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
	}]);

