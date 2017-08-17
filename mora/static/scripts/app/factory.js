'use strict';
/* Controllers */

angular.module('moApp.factory', [])
    .factory('myHttpInterceptor', [
        '$q', 'sysLog', 'localStorageService',
        function($q, sysLog, localStorageService) {
        return {
            response: function (response) {
                // do nothing
                return response;
            },
            responseError: function (response) {
                // do error logging
                if((response.status == '404') || (response.status == '400')|| (response.status == '0')){
                	return $q.reject(response);
                }else if(response.status == '401'){
                    localStorageService.remove('moUserAuth');
                    sysLog.record("Unauthorized access!", response, 'debug', false);
                    return $q.reject(response); 
                }else{
                	sysLog.record("Error in fetching '"+ response.config.url+"'", response, 'debug', true);
                	return $q.reject(response);
    	        }
            }
        };
    }])
    .factory('tokenInjector', ['localStorageService', function(localStorageService) {
        var tokenInjector = {
            request: function(config) {
                if (localStorageService.get("moUserAuth")) {
                    var isLoggedIn = localStorageService.get("moUserAuth");
                    config.headers['X-AUTH-TOKEN'] = isLoggedIn["authToken"];
                }
                return config;
            }
        };
        return tokenInjector;
    }])
    .factory("loginFactory", function($q, $http, sysService) {
        var deffered = $q.defer();
        var outData = {"response": false, "data": ""};
        return {
            // Login  //////////////////////////////////////////////////////
            in : function(u, p, r){
                var deffered = $q.defer();
                $http.post('service/user/'+u+'/login', { password: p, _spring_security_remember_me :  r}).then(
                    function(response) { deffered.resolve(response); },
                    function(error) { deffered.resolve(error);}
                )
                return deffered.promise;
            },
            // Logout  //////////////////////////////////////////////////////
            out : function(u){
                var deffered = $q.defer();
                $http.post('service/user/'+u+'/logout').then(
                    function(response) { deffered.resolve(response); },
                    function(error) { deffered.resolve(error);}
                )
                return deffered.promise;
            },
            // Login  //////////////////////////////////////////////////////
            acl : function(u,p){
                var deffered = $q.defer();
                $http.post('acl/').then(
                    function(response) { deffered.resolve(response); },
                    function(error) { deffered.resolve(error);}
                )
                return deffered.promise;
            }
        } 
    })
    .factory("sysFactory", function($q, $http) {
        var deffered = $q.defer();
        var langData = {"response": false, "data": ""};
        var langi18Keys = {"response": false, "data": ""};
        return {
            // Load Languages  //////////////////////////////////////////////////////
            langs : function(){
                var deffered = $q.defer();
                $http.get('translation/lang.json')
                .success(function(data) {
                    langData.response = true;
                    langData.data = data.languages;
                    deffered.resolve();
                }).
                error(function(data){
                    langData.response = false;
                    deffered.resolve();
                });
                return deffered.promise;
            },
            langsRes : function(){ return langData; },
            // Load Tabs  //////////////////////////////////////////////////////
            langKeys : function(url){
                var deffered = $q.defer();
                $http.get(url)
                .success(function(data) {
                    langi18Keys.response = true;
                    langi18Keys.data = data.translations;
                    deffered.resolve();
                }).
                error(function(data){
                    langi18Keys.response = false;
                    deffered.resolve();
                });
                return deffered.promise;
            },
            langKeysRes : function(){ return langi18Keys; },
            // Load Org  //////////////////////////////////////////////////////
            historyLog : function(url){
                return $http.get(url, {params:{'t': _.now()}}).then(
                    function(response){ return response.data; },
                    function(error){ return $q.reject(error); }
                );
            }
        } 
    })
    .factory("empFactory", function($q, $http) {
        var deffered = $q.defer();
        var empInfo = {"response": false, "data": ""};
        var empCre = {"response": false, "data": ""};
        return {
            // Load Employees  //////////////////////////////////////////////////////
            employeeList : function(data){
                return $http.get("e/", {"params": data, cache: true}).then(
                    function(response){ return response.data; },
                    function(error){ return $q.reject(error); }
                );
            },
            // Load Tabs  //////////////////////////////////////////////////////
            empHeaders : function(){
                return $http.get('partials/employee/viewHeader.json', {cache: true}).then(
                    function(response){ return response.data; },
                    function(error){ return $q.reject(error); }
                );
            },
            // Load Emp  //////////////////////////////////////////////////////
            empInfos: function(uuid){
                var deffered = $q.defer();
                $http.get('e/' + uuid, {cache: true})
                .success(function(data) {
                    empInfo.response = true;
                    empInfo.data = data;
                    deffered.resolve();
                }).
                error(function(data){
                    empInfo.response = false;
                    deffered.resolve();
                });
                return deffered.promise;
            },
            empInfosRes: function(){ return empInfo; },
            // Emp info by CPR  ////////////////////////////////////////////////
            empInfosByCPR : function(cpr){
                return $http.get('e/'+cpr).then(
                    function(response){ return response.data; },
                    function(error){ return $q.reject(error); }
                );
            },
            // Create Emp  ////////////////////////////////////////////////////
            empCreate: function(section, uuid, json){
                var deffered = $q.defer();
                var url = 'e/'+uuid+'/role-types/'+section;
                $http.post(url, json)
                .success(function(data) {
                    empCre.response = true;
                    empCre.data = data;
                    deffered.resolve();
                }).
                error(function(data){
                    empCre.response = false;
                    empCre.data = data;
                    deffered.resolve();
                });
                return deffered.promise;
            },
            // Update Org Role  ////////////////////////////////////////////////
            empCreateNew: function(url, json, callback){
                var deffered = $q.defer();
                $http.post(url, json).success(function(data, status, headers, config) {
                  deffered.resolve(true);
                  callback(true, data);
                }).error(function(data, status, headers, config) {
                  deffered.resolve(false);
                  callback(false, data);
                });
                return deffered.promise;
            },
            empCreateRes: function(){ return empCre; },
            // Emp Roles  //////////////////////////////////////////////////////
            empRoles : function(uuid, roleType, date, validity){
				date = angular.isDefined(date)?date:'';
				validity = angular.isDefined(validity)?validity:'';
                return $http.get('e/'+uuid+'/role-types/'+roleType+'/?validity='+validity+'&effective-date='+date, { params: { 't': new Date().getTime() } }).then(
                    function(response){ return response.data; },
                    function(error){ return $q.reject(error); }
                );
            },
            // Emp End  //////////////////////////////////////////////////////
            empEnd : function(uuid, date, callback){
                var url = 'e/'+uuid+'/actions/terminate';
                var deffered = $q.defer();            
                $http({
                  url     : url,
                  method  : 'POST',
                  params  : {
                    'date' : date
                  }
                }).
                success(function(data, status, headers, config) {
                  deffered.resolve(data);
                  callback(true, data);
                }).
                error(function(data, status, headers, config) {
                  deffered.resolve(data);
                  callback(false, data);
                });
            },
            // Emp Move  //////////////////////////////////////////////////////
            empMove : function(uuid, date, unit, data, callback){
                var deffered = $q.defer();            
                $http.post('e/'+uuid+'/actions/move?org-unit='+unit+'&date='+date, data)
                .success(function(data, status, headers, config) {
                  deffered.resolve(data);
                  callback(true, data);
                }).
                error(function(data, status, headers, config) {
                  deffered.resolve(data);
                  callback(false, data);
                });
            },
            // Update Org Role  ////////////////////////////////////////////////
            empUpdateRole: function(key, empUUID, rowUUID, json){
                var deffered = $q.defer();
                var url = "e/"+empUUID+"/role-types/"+key+"/"+rowUUID;
                var deffered = $q.defer();            
                $http.post(url, json).then(
                    function(response) { deffered.resolve(response); },
                    function(error) { deffered.resolve(error);}
                )
                return deffered.promise;
            }
        } 
    })
    .factory("orgFactory", function($q, $http, $cacheFactory) {
        var deffered = $q.defer();
        var orgInfo = {"response": false, "data": ""};
        var orgCre = {"response": false, "data": ""};
        var orgListData = {};
        return {
            // Load Org  //////////////////////////////////////////////////////
            orgList : function(uuid, date, query, timestamp){
                if(!angular.isDefined(uuid)){
                    return $http.get('o', {cache: true}).then(
                        function(response){ 
                            orgListData = response;
                            return response.data; },
                        function(error){ return $q.reject(error); }
                    );
                }else{
                    date = angular.isDefined(date)?date:'';
                    query = angular.isDefined(query)?query:'';
                    timestamp = angular.isDefined(timestamp)?'&t='+_.now():'';
                    return $http.get('o/'+uuid+'/full-hierarchy?effective-date='+date+'&query='+query+''+timestamp, {cache: true}).then(
                        function(response){ return response.data; },
                        function(error){ return $q.reject(error); }
                    );
                }
            },
            // Load Org  //////////////////////////////////////////////////////
            orgListSpecificTreeType : function(uuid, date, query, treeType, timestamp){
                if(!angular.isDefined(uuid)){
                    return $http.get('o', {cache: true}).then(
                        function(response){ 
                            return response.data; },
                        function(error){ return $q.reject(error); }
                    );
                }else{
                    date = date ? date:'';
                    query = query ? query:'';
                    var cache = {cache: true};
                    timestamp = angular.isDefined(timestamp)?'&t='+_.now():'';
                    if(timestamp != ""){
                        cache = {cache: false};
                        var ch = $cacheFactory.get('$http');
                        ch.remove('o/'+uuid+'/full-hierarchy?effective-date='+date+'&query='+query+'&treeType='+treeType)
                    }
                    return $http.get('o/'+uuid+'/full-hierarchy?effective-date='+date+'&query='+query+'&treeType='+treeType+''+timestamp, cache).then(
                        function(response){ 
//                            if(response.data.hierarchy.hasChildren){
//                                response.data.hierarchy.children.push({children:[]})
//                            }

                            return response.data; 
                        },function(error){ return $q.reject(error); 
                    });
                }
            },
           
            // Load Organisation  //////////////////////////////////////////////
            organisationList : function(data){
                var orgUnit = orgListData.data[0].uuid;
                return $http.get("o/"+orgUnit+"/org-unit/", {"params": data, cache: true}).then(
                    function(response){ return response.data; },
                    function(error){ return $q.reject(error); }
                );
            },
            // Org info by CPR  ////////////////////////////////////////////////
            orgInfos : function(uuid, date){
                var orgUnit = orgListData.data[0].uuid;
                date = angular.isDefined(date)?date:'';
                return $http.get('o/'+orgUnit+'/org-unit/?query='+uuid+'&effective-date='+date).then(
                    function(response){ return response.data; },
                    function(error){ return $q.reject(error); }
                );
            },
            // Load Tabs  //////////////////////////////////////////////////////
            orgHeaders : function(){
                return $http.get('partials/organisation/viewHeader.json', {cache: true}).then(
                    function(response){ return response.data; },
                    function(error){ return $q.reject(error); }
                );
            },
            orgEnd : function(orgId, searchedId, date, callback){
                var url = 'o/'+orgId+'/org-unit/'+searchedId;   
                var deffered = $q.defer();            
                $http({
                  url     : url,
                  method  : 'DELETE',
                  params  : {
                    'endDate' : date
                  }
                }).
                success(function(data, status, headers, config) {
                  deffered.resolve(data);
                  callback(true, data);
                }).
                error(function(data, status, headers, config) {
                  deffered.resolve(data);
                  callback(false, data);
                });
            },
            orgMove : function(fromId, sDate, toId, orgId, callback){
                var url = 'o/'+orgId+'/org-unit/'+fromId+'/actions/move';   
                var deffered = $q.defer();            
                $http({
                  url     : url,
                  method  : 'POST',
                  data : {
                    'moveDate'   : sDate,
                    'newParentOrgUnitUUID' : toId
                  }
                }).
                success(function(data, status, headers, config) {
                  deffered.resolve(data);
                  callback(true, data);
                }).
                error(function(data, status, headers, config) {
                  deffered.resolve(data);
                  callback(false, data);
                });
            },
            orgRename : function(orgId, orgUnitId, data, callback){
                var url = 'o/'+orgId+'/org-unit/'+orgUnitId+'?rename=true';
                var deffered = $q.defer();            
                $http({
                  url     : url,
                  method  : 'POST',
                  data    : data
                }).
                success(function(data, status, headers, config) {
                  deffered.resolve(data);
                  callback(true, data);
                }).
                error(function(data, status, headers, config) {
                  deffered.resolve(data);
                  callback(false, data);
                });
            },
            // Create Org  ////////////////////////////////////////////////////
            orgCreate: function(section, uuid, json){
                var deffered = $q.defer();
                var orgUnit = orgListData.data[0].uuid;
                var url = 'o/'+orgUnit+'/org-unit/'+uuid+'/role-types/'+section;
                if(section === "location"){
                    url = 'o/'+orgUnit+'/org-unit/'+uuid+'/role-types/'+section;
                }
                $http.post(url, json).then(
                    function(response) { deffered.resolve(response); },
                    function(error) { deffered.resolve(error);}
                )
                return deffered.promise;
            },
            orgCreateContactChannnel: function(orgUUID, key, rowUUID, json){
                var deffered = $q.defer();
                var orgUnit = orgListData.data[0].uuid;
                var url = 'o/'+orgUnit+'/org-unit/'+orgUUID+'/role-types/'+key+'/'+rowUUID;
                $http.post(url, json).then(
                    function(response) { deffered.resolve(response); },
                    function(error) { deffered.resolve(error);}
                )
                return deffered.promise;
            },
            // Org Roles  //////////////////////////////////////////////////////
            orgRoles : function(uuid, roleType, date, validity, unique){
                var orgUnit = orgListData.data[0].uuid;
                date = angular.isDefined(date)?date:'';
                unique = angular.isDefined(unique)?'&unique=true':'';
                validity = angular.isDefined(validity)?validity:'';
                var url = 'o/'+orgUnit+'/org-unit/'+uuid+'/role-types/'+roleType+'/?validity='+validity+'&effective-date='+date+''+unique;
                if(roleType === "org-unit"){
                    url = 'o/'+orgUnit+'/org-unit/'+uuid+'/?validity='+validity+'&effective-date='+date
                }
                return $http.get(url, { params: { 't': new Date().getTime() } }).then(
                    function(response){ return response.data; },
                    function(error){ return $q.reject(error); }
                );
            },
            // Update Org Role  ////////////////////////////////////////////////
            orgUpdateRole: function(orgUUID, key, rowUUID, json){
                var deffered = $q.defer();
                var orgUnit = orgListData.data[0].uuid;
                var url = 'o/'+orgUnit+'/org-unit/'+orgUUID+'/role-types/'+key+'/'+rowUUID;
                if(key === "org-unit"){
                    url = 'o/'+orgUnit+'/org-unit/'+orgUUID;
                }else if(key === "contact-channel"){
                    url = 'contact-channel/'+rowUUID;
                }

                $http.post(url, json).then(
                    function(response) { deffered.resolve(response); },
                    function(error) { deffered.resolve(error);}
                )
                return deffered.promise;
            },
            // Org Locations /////////////////////////////////////////////////
            orgLocations: function(uuid){
                var orgUnit = orgListData.data[0].uuid;
                return $http.get('o/'+orgUnit+'/org-unit/'+uuid+'/role-types/location').then(
                    function(response){ return response.data; },
                    function(error){ return $q.reject(error); }
                );
            }
        } 
    });