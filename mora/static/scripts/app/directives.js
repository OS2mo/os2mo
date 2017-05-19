'use strict';

/* Directives */


angular.module('moApp.directives', [])
	.directive('autoFillSync', function($timeout) {
		return {
		  require: 'ngModel',
		  link: function(scope, elem, attrs, ngModel) {
		      var origVal = elem.val();
		      $timeout(function () {
		          var newVal = elem.val();
		          if(ngModel.$pristine && origVal !== newVal) {
		              ngModel.$setViewValue(newVal);
		          }
		      }, 500);
		  }
		}
	})
	.directive('loadingContainer', function () {
	    return {
	        restrict: 'A',
	        scope: false,
	        link: function(scope, element, attrs) {
	            var loadingLayer = angular.element('<div class="loading"></div>');
	            element.append(loadingLayer);
	            element.addClass('loading-container');
	            scope.$watch(attrs.loadingContainer, function(value) {
	                loadingLayer.toggleClass('ng-hide', !value);
	            });
	        }
	    };
	})
	.directive('acl',['sysService', function (sysService) {
	    return {
            restrict: 'A',
            link: function ($scope, element, attrs) {
                var acl = attrs.acl;
                acl = acl.split('|');
                var permissions = sysService.setupACL.get()
                permissions = permissions['/' + acl[0] + '/**'];

                if (permissions) {
                    permissions = permissions.split(', ');
                    var access = _.filter(permissions, function (rw) {
                        return rw == acl[1];
                    });
                    if (access.length == 0) {
                        element.remove();
                    }
                }
            }
	    }
    }])
    .directive('tooltipTree', ['$compile', '$timeout', '$http', '$q', function($compile, $timeout, $http, $q) {
	    return {
	      restrict: 'A',	
	      replace : false,	
	      link: function(scope, elem, attrs) {	 
	      	scope.resData = "Loading...";
	      	scope.show = false;
	      	scope.loading = true;
	      	var data = JSON.parse(attrs.tooltipTree);	
			
	       	var html = "";
            html = html+'<div class="popover bottom tree" style="display: block; margin-top: 25px;" ng-show="show">';
            html = html+'<div class="arrow"></div>';
            html = html+'<div class="popover-inner">';
            html = html+'<div class="popover-content" ng-show="loading">Loading...</div>';
            html = html+'<div class="popover-content tree-classic" ng-show="!loading"><ul class="orgTreeSelectorList" ng-tree=\"resData\"><li>{{item.name}}</li></ul></div>';
            html = html+'</div>';
            html = html+'</div>';
            html = html+'</div>';

            var e = $compile(html)(scope);
            elem.after(e);
			elem.parent().bind('mouseenter', function() {
				scope.show = true;
				var deferred = $q.defer();
		      	$http.get('o/'+data.org+'/full-hierarchy', 
					{ params: { orgUnitId: data['uuid'], 'effective-date':data['valid-from']},
					timeout: deferred.promise, cache: true }
				).then(function(response){
					scope.loading = false;
					scope.resData = [response.data.hierarchy];
				});
            });
            elem.parent().bind('mouseleave', function() {
                scope.show = false;
                scope.$parent.show = false;
            });
	      }	    
	    };
	}])
	.directive( 'clickhandler',['$document', '$timeout', function($document, $timeout){
		var fn = {
	      	link: function(scope, elem, attrs) {
		      	var attributes = attrs;
		      	$document.bind('click', function(ev) {
			       if(ev.target.className.indexOf("tree") < 0){
			       		$timeout(function(){
			       			scope.$broadcast('hideTypeAheadTree');
			       		},100)
			       		
			       }
			    });	        
		    }
	    };
	    return fn;
	}])
	.directive( 'orgtypeaheadtree',['$compile', 'sysService', '$http', '$q', 'orgFactory', '$filter', function($compile, sysService, $http, $q, orgFactory, $filter) {
		return {
	      restrict: 'E',	
	      replace : true,	
	      link: function(scope, elem, attrs) {	


            // Load Orgs and OrgUnits
			sysService.orgList.fetch('treeType').then(function(response){
				scope.organizations = response;
				var date = (angular.isDefined(attrs.datetype) && attrs.datetype != "")?$filter('date')(attrs.datetype, "dd-MM-yyyy"):"";
				sysService.loadOrgData.getUnits(date,'treeType').then(function(response) {
		            scope.orgUnits = response;
		            _createTree();
		        });
			});
  	    	scope.attributes = attrs;

  	    	function _createTree(){
		  	    scope.treeOptions = {
				    nodeChildren: "children",
				    dirSelectable: true,
				    injectClasses: {
				        ul: "a1",
				        li: "a2",
				        liSelected: "a7",
				        iExpanded: "fa fa-folder-open",
				        iCollapsed: "fa fa-folder",
				        iLeaf: "fa fa-file",
				        label: "a6",
				        labelSelected: "a8"
				    }
				};
				var orgId = scope.attributes.orgid ? scope.attributes.orgid : scope.organizations[0].uuid;
				scope.treeModel = scope.orgUnits[orgId];
				scope.isTypeAhead = false;

				if(scope.attributes.treeorigin){
					scope.addNode(scope.treeModel[0], true);
					scope.expandedNodes = [scope.treeModel[0]];	
				}
				treeView();
		       	
  	    	};

  	    	function treeView(){
		       	var html = '<div class="type-ahead-tree" style="top: 100%;left: 146px;z-index: 1000;position: absolute;float: left;min-width: 160px;padding: 5px 0;margin: 2px 0 0;list-style: none;font-size: 14px;text-align: left;background-color: #fff;border: 1px solid #ccc;border: 1px solid rgba(0,0,0,.15);border-radius: 4px;-webkit-box-shadow: 0 6px 12px rgba(0,0,0,.175);box-shadow: 0 6px 12px rgba(0,0,0,.175);background-clip: padding-box;">'+		            					            	
			                   	'<treecontrol class="tree-classic"'+
			   	                    'tree-model="treeModel"'+
			   	                    'options="treeOptions"'+
			   	                    'selected-node="selectedNode"'+
			   	                    'on-node-toggle="addNode(node, expanded, false, null, $event)"'+
			   	                    'on-selection="selectNode(node,attributes.inputtreetype)"'+
			   	                    'expanded-nodes="expandedNodes">'+
			   	                    '{{node.name}}'+
			                   	'</treecontrol>'+				               	
		               		'</div>';
	            var e = $compile(html)(scope);
	            elem.after(e);
  	    	};

  	    	scope.$on("reloadTreeData", function(event, data){
  	    		sysService.orgList.fetch('treeType').then(function(response){
					scope.organizations = response;
					var date = (angular.isDefined(attrs.datetype) && attrs.datetype != "")?$filter('date')(attrs.datetype, "dd-MM-yyyy"):"";
					sysService.loadOrgData.getUnits(date,'treeType',true).then(function(response) {
			            scope.orgUnits = response;
			            
						var orgId = scope.attributes.orgid ? scope.attributes.orgid : scope.organizations[0].uuid;
						scope.treeModel = scope.orgUnits[orgId];
						scope.isTypeAhead = false;

						if(scope.attributes.treeorigin){
							scope.addNode(scope.treeModel[0], true, true, date);
							scope.expandedNodes = [scope.treeModel[0]];	
						}
			        });
				});
  	    	});
  	    	
  	    	scope.$on("timemachineTypeAheadData", function(event, data){
  	    		if(scope.attributes.orgid){
  	    			if(data.response[0].org !== scope.attributes.orgid){
	  	    			return false;
	  	    		}
  	    		}
  	    		scope.isTypeAhead = false;
  	    		scope.treeModel = data.response;

  	    		angular.forEach(scope.treeModel, function(value, key){
            		var orgId = scope.attributes.orgid ? scope.attributes.orgid : scope.organizations[0].uuid;
            		scope.addNode(value, true, true, data.date);
					scope.expandedNodes = [value];	       
	            });
  	    	});

  	    	scope.$on("typeAheadData", function(event, data){
  	    		if(scope.attributes.orgid){
  	    			if(data[0].org !== scope.attributes.orgid){
	  	    			return false;
	  	    		}
  	    		}
  	    		scope.isTypeAhead = true;
  	    		scope.treeModel = data;
  	    		angular.forEach(scope.treeModel, function(value, key){
            		scope.expandedNodes.push(value);
					if(value.children && value.children.length){
						setindex(value);
					}         
	            });
  	    	});

  	    	var setindex = function(unitData){
				scope.expandedNodes.push(unitData);
				angular.forEach(unitData.children, function(unit,index){
					if(unit.children && unit.children.length){
						setindex(unit);
					}
				});
				return unitData;
			}

  	    	scope.addNode = function(node, isExpanded, timestamp, effectiveDate, event){  
	  	    	if(scope.isTypeAhead){
	  	    		return;
	  	    	}else if(!isExpanded){
  	    			node.children.length = 1;
  	    		}else{
	  	    		var orguuid = scope.organizations[0].uuid;
	  	    		var date = (angular.isDefined(attrs.datetype) && attrs.datetype != "")?$filter('date')(attrs.datetype, "dd-MM-yyyy"):"";
	  	    		if(angular.isDefined(effectiveDate) && effectiveDate != ""){
	  	    			date = effectiveDate;
	  	    		}
					sysService.orgTreeListSpecificType(orguuid,date, '', '', node.uuid, timestamp, function(newChildrens){
						addChild(node, newChildrens);	
					});	
  	    		}
  	    	};
  	    	function addChild(selectedNode, newChildrens){
  	    		selectedNode.children = newChildrens;   	    		
  	    	};
	  	    
	      }	    
	    };
	}]);
