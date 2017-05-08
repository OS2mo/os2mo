'use strict';
	angular.module('moApp.directives')
	.directive( 'treeModel1111', ['$compile', 'sysService', 'orgFactory', '$rootScope', '$location', function( $compile, sysService,orgFactory,  $rootScope, $location) {
		return {
			restrict: 'A',
			scope: true,
 			transclude: true,
 			link: function ( scope, element, attrs ) {
 				console.log(attrs)
				//tree id
				var treeId = attrs.treeId;
				//tree model
				var treeUnit = attrs.treeUnit;
				//tree Type
				var treeType = attrs.treeType;
				//selected node
 				var nodeSelected = attrs.nodeSelected;
 				//effective date
 				var treeEffectiveDate = attrs.treeEffectiveDate || '';
				//node id
				var nodeId = attrs.uuid || 'uuid';
				//node label
				var nodeLabel = attrs.nodeLabel || 'name';
				//children
				var nodeChildren = attrs.nodeChildren || 'children';
				var currentNode = [];

				//tree model
				orgFactory.orgList(treeUnit, treeEffectiveDate).then(function(units) {
                	scope.treeModel = [units.hierarchy];
            	});

          		var _loadTreeView = function(){
          			/*var template = '<ul class="first">'+
          				'<li data-ng-repeat="node in treeModel track by $index">{{node}} {{$index}}</div>'+
						'<li bindonce data-ng-class="[node.current, node.selected]" data-ng-repeat="node in ' + scope.treeModel + ' track by $index">'+
						'</li>' +
					'</ul>';*/

	 				var template = '<ul class="first">' +
						'<li bindonce data-ng-class="[node.current, node.selected]" data-ng-repeat="node in treeModel track by $index">'+
							'<i class="fa fa-folder collapsed" data-ng-if="node.' + nodeChildren + '.length && !node.collapsed" data-ng-click="' + treeId + '.selectNodeHead(node)"></i> ' +
							'<i class="fa fa-folder-open expanded" data-ng-if="node.' + nodeChildren + '.length && node.collapsed" data-ng-click="' + treeId + '.selectNodeHead(node)"></i> ' +
							'<i class="fa fa-file normal" data-ng-hide="node.' + nodeChildren + '.length"></i> ' +
							'<span data-ng-class="node.selected" data-ng-click="' + treeId + '.selectNodeLabel(node)">{{node.' + nodeLabel + '}}</span>' +
							//'{{node.children}}';
							/*'<div data-angular-treeview="true" ' +
							'data-ng-hide="'+treeId+'.nodeCollapsed(node, nodeSelected)" ' +
							'data-tree-type="'+ treeType +'" ' +
							'data-tree-id="' + nodeId + '" ' +
							'data-tree-model="" ' +
							'data-tree-unit="'+ treeUnit +'" ' +
							'data-node-selected="' + nodeSelected + '" ' +
							'data-tree-effective-date="' + treeEffectiveDate + '">' +*/
							//'<div data-ng-hide="'+treeId+'.nodeCollapsed(node, nodeSelected)" data-tree-id="' + treeId + '" data-tree-model="node.' + nodeChildren + '" data-node-id=' + nodeId + ' data-node-label=' + nodeLabel + ' data-node-selected=' + nodeSelected + ' data-node-children=' + nodeChildren + ' data-tree-effective-date=' + treeEffectiveDate + '></div>' +
						'</li>' +
					'</ul>';

					//check tree id, tree model
					if( treeId && scope.treeModel ) {
						//root node
						if( attrs.angularTreeview ) {
							//create tree object if not exists
							scope[treeId] = scope[treeId] || {};
							scope[treeId].selNode = "";
							//if node head clicks,
							scope[treeId].selectNodeHead = scope[treeId].selectNodeHead || function( selectedNode ){
								//Collapse or Expand
								selectedNode.collapsed = !selectedNode.collapsed;
							};
							scope[treeId].nodeCollapsed = function( node ){
								node.current = undefined;
								if(node.uuid == nodeSelected){
									currentNode = [];
									node.current = 'current';
									return node.collapsed;
								}else{
									// To keep tree expanded
									if(nodeSelected != ""){
										return node.collapsed;
									}else{
										node.current = undefined;
										return !node.collapsed;
									}
								}
							};
							////////////////////////
							scope.$watch( treeId+'.selNode', function( newObj, oldObj ) {
							    if( scope[treeId].selNode && angular.isObject(scope[treeId].selNode) ) {
							        scope[treeId].selectNodeLabel(scope[treeId].selNode);
							        sysService.recordEvent.set("debug", scope[treeId]);
							    }
							}, false);
							//if node label clicks,
							scope[treeId].selectNodeLabel = scope[treeId].selectNodeLabel || function( selectedNode ){
								if(selectedNode.selected == "selected"){ //remove highlight of selected node
									selectedNode.selected = undefined;
									//currentNode = _.without(currentNode, selectedNode.uuid);
									currentNode = '';
								}else{ //set highlight to selected node
									selectedNode.selected = 'selected';
									//currentNode.push(selectedNode.uuid);
									//currentNode = _.uniq(currentNode);
									currentNode = selectedNode;
									if(treeType != "timeMachine")
										$location.path("organisation/"+selectedNode.uuid);
								}

								//set currentNode
								scope[treeId].currentNode = currentNode;
								scope.$emit('currentNode', scope[treeId].currentNode);
							};
						}
						//Rendering template.
						//element.html('').append( $compile( template )( scope ) );
					}
					element.html('').append( $compile( template )( scope ) );
          		}

				attrs.$observe("nodeSelected",function(n,o){
             		nodeSelected = (!n)?'':n;
             		sysService.recordEvent.set("debug", "Node selected "+ nodeSelected );
          		});

          		attrs.$observe("treeEffectiveDate",function(n,o){
          			if(angular.isDefined(n) && n != ""){
          				orgFactory.orgList(treeUnit, n).then(function(units) {
		                	scope.treeModel = [units.hierarchy];
		            	});
             		}
          		});

          		if(attrs.treeModel == ""){ // If no data coming
          			scope.$watch('treeModel', function(n, o){
	          			console.log("asdfsdfsdf")
	          			if(angular.isDefined(scope.treeModel) && scope.treeModel != ""){
	          				_loadTreeView();
	          			}
          			})
          		}else{
          			console.log("NO http")
          			scope.treeModel = attrs.treeModel;
          			_loadTreeView();
          		}
          		
				
			}
		};
	}])
	.directive('orgTreeInput', function() {
        var directive = {
        	link: function(scope, elem, attrs) {
		        scope.moveString = attrs.element;
		        scope.treeindex = (attrs.treeindex)?attrs.treeindex:'';
			}
        };
        directive.restrict = 'E'; /* restrict this directive to elements */
        directive.template = '';
        directive.template += '<div class="input-group orgTreeInputSelector">';
        directive.template += '     <input bindonce type="text" tabindex="{{treeindex}}" name="empObj.org_unit.uuid" ng-model="query" placeholder="{{i18n.orgtreeinput_placeholder}}" typeahead="unit.name for unit in getOrgUnitInputTree($viewValue) | filter:$viewValue | limitTo:10" typeahead-loading="loadingOrgUnits" typeahead-min-length="3" typeahead-on-select="orgUnitSelect($item, $model, $lable); query = node.name; $item = node;" class="form-control input-sm" autocomplete="off" typeahead-wait-ms="1000" typeahead-template-url="orgUnitTreeSelector.html" ng-disabled="$parent.treeDisabled" required>';
        directive.template += '     <span class="input-group-btn">';
        directive.template += '     <button type="button" class="btn btn-default search" id="orgUnitSearchBtn">';
        directive.template += '         <i ng-hide="loadingOrgUnits" class="fa fa-search"></i>';
        directive.template += '         <i ng-show="loadingOrgUnits" class="refresh"></i>';
        directive.template += '     </button>';
        directive.template += ' </span>';
        directive.template += '</div>';
        return directive;
    }).directive('orgTreeInputField', function() {
        var directive = {
        	link: function(scope, elem, attrs) {
		        scope.moveString = attrs.element;
		        scope.treeindex = (attrs.treeindex)?attrs.treeindex:'';
		        scope.isDateSelected = (attrs.date) ? attrs.date : false;
		        scope.$on('dateSelected',function(ev, data){
		        	scope.isDateSelected = false;
		        });		        
			}
        };
        directive.restrict = 'E'; /* restrict this directive to elements */       
        directive.template = '';
        directive.template += '<div class="input-group orgTreeInputSelector">';
        directive.template += '     <input ng-disabled="isDateSelected" bindonce type="text" tabindex="{{treeindex}}" name="org_unit" ng-model="query" placeholder="{{i18n.orgtreeinputfield_placeholder}}" typeahead="unit.name for unit in getOrgUnitInputTree($viewValue) | filter:$viewValue | limitTo:10" typeahead-loading="loadingOrgUnits" typeahead-min-length="3" typeahead-on-select="orgUnitSelect($item, $model, $lable); query = node.name; $item = node;" class="form-control input-sm" autocomplete="off" typeahead-wait-ms="1000" typeahead-template-url="orgUnitTreeSelectorField.html">';
        directive.template += '     <span class="input-group-btn">';
        directive.template += '     <button type="button" class="btn btn-default search" id="orgUnitSearchBtn">';
        directive.template += '         <i ng-hide="loadingOrgUnits" class="fa fa-search"></i>';
        directive.template += '         <i ng-show="loadingOrgUnits" class="refresh"></i>';
        directive.template += '     </button>';
        directive.template += ' </span>';
        directive.template += '</div>';
        return directive;
    });



