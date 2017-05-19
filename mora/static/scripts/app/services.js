'use strict';

/* Services */

angular.module('moApp.services', ['ngCookies','ngRoute']).
  value('version', '0.1')
  .service('sysService', ['sysLang', '$rootScope', '$location', 'orgFactory', '$q', '$log', 'sysAuth', '$http', function(sysLang, $rootScope, $location, orgFactory, $q, $log, sysAuth, $http){
        var _this = this;
        
        // Store global accessible data ////
        _this.shortcuts = {
            "help": {"key": "h", "title": "Help"},
            "login": {"key": "l", "title": "Login"},

            "employeeWorkflowNew": {"key": "ctrl+alt+n", "title": "New Employee Workflow"},
            "employeeWorkflowEnd": {"key": "ctrl+alt+x", "title": "End Employee Workflow"},
            "employeeWorkflowMove": {"key": "ctrl+alt+m", "title": "Move Engagement Workflow"},
            "employeeWorkflowMoveMany": {"key": "ctrl+alt+y", "title": "Move Many Engagement Workflow"},
            "employeeWorkflowAbsence": {"key": "ctrl+alt+o", "title": "Absence Workflow"},
            "employeeView": {"key": "ctrl+alt+v", "title": "View Employee"},
            "employeeEdit": {"key": "ctrl+alt+e", "title": "Edit employee"},

            "organisationWorkflowNew": {"key": "ctrl+alt+n", "title": "New Organisation Unit Workflow"},
            "organisationWorkflowEnd": {"key": "ctrl+alt+d", "title": "End Organisation Unit Workflow"},
            "organisationWorkflowMove": {"key": "ctrl+alt+m", "title": "Move Organisation Unit Workflow"},
            "organisationWorkflowRename": {"key": "ctrl+alt+r", "title": "Rename Organisation Unit Workflow"},
            "organisationView": {"key": "ctrl+alt+v", "title": "View Organisation Unit"},
            "organisationEdit": {"key": "ctrl+alt+e", "title": "Edit Organisation Unit"},


            "popupSubmit": {"key": "enter", "title": "Save changes"},
            "popupClose": {"key": "esc", "title": "Close modal"}
        };

        _this.state;
        _this.path = window.location.pathname;

        _this.dateFormat = {
            format: "dd-MM-yyyy",
            editFormat: "dd-MM-yyyy",
            mask: "99-99-9999",
            placeholder: "DD-MM-YYYY",
            validateInput : function(date){
                //if(/^([0-9]{2})-([0-9]{2})-([0-9]{4})$/.test(date)){
                if(date instanceof Date){
                    return true;
                }else{
                    return false;
                }
            }
        };

        _this.makeDate = function(date){
            //if(date instanceof Date){ return date; }
            var parts = date.split("-");
            var dt = new Date();
            dt.setDate(parseInt(parts[0]));
            dt.setMonth(parseInt(parts[1]));
            dt.setYear(parseInt(parts[2]));
            dt.setDate(dt.getDate()-1);
            return dt;
        }

        _this.empList = new Object(); 
        _this.orgList = {
            data: [],
            get: function(){
                return this.data;
            },
            fetch: function(treeType){
                if(angular.isDefined(treeType)){
                    return orgFactory.orgListSpecificTreeType().then(function(response) {
                        return response
                    });
                }else{
                    return orgFactory.orgList().then(function(response) {
                        return response
                    });
                }
                
            }
        };

        _this.orgUnitList = {
            data: [],
            get: function(key){
                if(key){
                    return this.data[key];
                }else{
                    return this.data;
                }
            },
            fetch: function(date, treeType, timestamp){
                var promOrgUnit = [];
                var treeData = [];
                if(angular.isDefined(treeType)){
                    angular.forEach(_this.orgList.data, function(value, key){
                        promOrgUnit.push(orgFactory.orgListSpecificTreeType(value.uuid, date, "", treeType, timestamp).then(function(units) {
                            treeData[value.uuid] = [units.hierarchy];
                        },function(error){
                        }));
                    });
                }else{
                    angular.forEach(_this.orgList.data, function(value, key){
                        promOrgUnit.push(orgFactory.orgList(value.uuid, date, '', timestamp).then(function(units) {
                            treeData[value.uuid] = [units.hierarchy];
                        },function(error){
                        }));
                    });
                }

                return $q.all(promOrgUnit).then(function () {
                    return treeData;
                });
            }
        }; 

        _this.loadOrgData = {
            set: function(){
                var promOrgUnit = [];
                var treeData = [];

                _this.orgList.fetch().then(function(response){
                    _this.orgList.data = response;
                    _this.orgUnitList.fetch().then(function(response){
                        _this.orgUnitList.data = response;
                    });
                });
            },
            getUnits: function(date, treeType, timestamp){
                var promOrgUnit = [];
                var treeData = [];
                return _this.orgUnitList.fetch(date, treeType, timestamp).then(function(response){
                    return response;
                });
            }
        }

        _this.setupACL = {
            perm: Array(),
            get: function(){
                return this.perm;
            },
            validate: function(perm){
                var acl = perm;
                acl = acl.split('|');
                var permissions = _this.setupACL.get()
                permissions = permissions['/'+acl[0]+'/**'];

                permissions = permissions.split(', ');
                var access = _.filter(permissions, function(rw){ 
                    return rw == acl[1]; });
                if(access.length == 0){
                    return false;
                }else{
                    return true;
                }

            },
            set: function(){
                var permission = sysAuth.getUserData()    
                permission = permission.acl;

                angular.forEach(permission, function(value, index){
                    if(value.url != '/acl'){ 
                        _this.setupACL.perm[value.url] = value.Privilegies;
                    }
                })
            }
        }

        _this.orgTreeListSpecificType = function(orguuid, date, query, treeType, nodeuuid, timestamp, callback){
            date = date ? date:'';
            query = query ? query:'';
            treeType = treeType ? treeType:'specific';
            var timestamp = angular.isDefined(timestamp)?'&t='+_.now():'';
            $http.get('o/'+orguuid+'/full-hierarchy?effective-date='+date+'&query='+query+'&treeType='+treeType+'&orgUnitId='+nodeuuid+''+timestamp, {cache: true}).then(
                function(response){ 
                    angular.forEach(response.data, function(value){
                        if(value.hasChildren){
                            value.children.push({children:[]})
                        }
                    });

                    callback(response.data); 
                },function(error){ 
                    return $q.reject(error); 
            });
        };
        ////////////////////////////////////
        _this.loadData = function(){
            _this.loadOrgData.set();
            _this.setupACL.set();
        }
        ///////////////////////////////////

        // Record system events
        this.recordEvent = {
            list : [],
            set : function(type, message){
                if(type == 'error') $log.warn(message);
                if(type == 'success') $log.info(message);
                if(type == 'debug') $log.debug(message);
                if(type != 'debug'){ this.list.unshift({'type': type, 'message': message}); }
            }, 
            get : function(){
                return this.list;
            },
            clean : function(){
                this.list = [];
            }
        }

        this.i18n = function(key){
            return sysLang.fetch(key);
        }

    }])

  .service('sysLog',["$log", "$rootScope", 'localStorageService', '$location', function(log, $rootScope, localStorageService, $location){
        this.record = function(message, response, state, display){
            var screenMsg = (display)?true:false;
            var status = response.status;
            var status = response.status;
            var config = response.config;
            var consoleMsg = "";
            consoleMsg =consoleMsg + message;
            consoleMsg =consoleMsg + "\nStatus code: "+status;
            
            /*if(state == ""){log(consoleMsg);} else if(state == "info"){log.info(consoleMsg);}
            else if(state == "warn"){log.warn(consoleMsg);}else if(state == "error"){ log.error(consoleMsg); 
            }else if(state == "debug"){ log.debug(consoleMsg); }*/

            if(status == "401" && config.method != "POST"){
                localStorageService.remove("moUserAuth");
                localStorageService.remove("loginTimeStamp");
                $location.path("/");
            }
            
            $rootScope.loggerMsg = {"show": false, "title": "", "content": "", "trace": ""};
            if(screenMsg){ //Display on screen
                message = message + " "+ config.method;
                $rootScope.loggerMsg = {"show": true, "title": "Status code #"+ status, "content": message, "trace": response.data.trace};
            }
        };
    }])
  
  .service('sysLang', function($rootScope, $http, localStorageService, sysFactory) {
        var _this = this;
    	_this.cookieLang = (localStorageService.get("lang")) ? localStorageService.get("lang") : "da_DK";
        $rootScope.i18n = "";

    	localStorageService.set("lang", _this.cookieLang);
    	this.loadLang = function(selected){
            if(angular.isDefined(selected)){ 
                localStorageService.set("lang", selected); 
                _this.cookieLang = selected;
            }else{
                _this.cookieLang = localStorageService.get("lang");
            }
            sysFactory.langKeys('translation/'+_this.cookieLang+'/i18n.json').then(function() {
                var res = sysFactory.langKeysRes();
                if(res.response){ // Success
                    $rootScope.i18n = res.data;
                    /*angular.forEach($rootScope.i18n, function(value, key){
                        $rootScope.i18n[key] = "<i18n/>"+ value;
                    })*/
                }
            });
        }; 

        this.fetch = function(key){
            return $rootScope.i18n[key];
        }   
    })

  .service('sysAuth', ['$rootScope', '$http', '$modal', '$q', 'localStorageService', function($rootScope, $http, $modal, $q, localStorageService) {
        var _this = this;
        _this.loginSection;
        _this.userIsAuthenticated = false;
        // Get user authentication /////////////////////////////////////////////
        this.getUserData = function() {
            return localStorageService.get('moUserAuth');
        };
        this.getUserAuthentication = function() {
            return (localStorageService.get('moUserAuth')) ? true : false;
        };
        this.setUserAuthentication = function(data, acl, rememberMe) {
            /*if(!$cookieStore.get("moUserAuth")){
                $cookieStore.put("moUserAuth", {"authToken": data.token, "authUser": data.user, "authRole": data.role[0], 'acl': acl});
                _this.userIsAuthenticated = true;
            }*/
            if(!localStorageService.get('moUserAuth')){
                localStorageService.set("moUserAuth", {"authToken": data.token, "authUser": data.user, "authRole": data.role[0], 'acl': acl, 'rememberMe': rememberMe});
                _this.userIsAuthenticated = true;
            }
        };
        this.unSetUserAuthentication = function(data) {
            /*$cookieStore.remove("moUserAuth");
            $cookieStore.remove("searched");*/
            localStorageService.remove("moUserAuth");
            localStorageService.remove("searched");
            localStorageService.remove("loginTimeStamp");
            _this.userIsAuthenticated = false;
        };
    }])

  .service('empService', ['$rootScope', '$http', '$modal', '$q', function($rootScope, $http, $modal, $q) {
    }]);
