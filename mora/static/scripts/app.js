'use strict';
// Declare app level module which depends on filters, and services
angular.module('moApp', [
  'ngRoute',
  'moApp.filters',
  'moApp.services',
  'moApp.directives',
  'moApp.controllers',
  'moApp.factory',
  'ui.bootstrap',
  'xeditable',
  'chieffancypants.loadingBar',
  'ngAnimate',
  'angularTree',
  'cfp.hotkeys',
  'ui.keypress',
  'ngTable',
  'treeControl',
  'LocalStorageModule'
])
.config(["localStorageServiceProvider","$locationProvider", "$stateProvider", "$urlRouterProvider", "$httpProvider", "cfpLoadingBarProvider", "datepickerPopupConfig", "hotkeysProvider",function(localStorageServiceProvider, $locationProvider, $stateProvider, $urlRouterProvider, $httpProvider, cfpLoadingBarProvider, datepickerPopupConfig, hotkeysProvider) {
  localStorageServiceProvider.setPrefix('moApp');
  localStorageServiceProvider.setStorageCookie(0, '/');   
  //localStorageServiceProvider.setStorageType('sessionStorage');

  $stateProvider
    .state('home', {
      url: "/",
      authenticate : false,
      data: {
        page: {"translation": false, "key": "home", "subKey": "", "title": "i18n.title_home"}
      },
      views: { 
        'header': { templateUrl: 'partials/common/header-login.html', controller: 'moHeader' },
        'main': { templateUrl: 'partials/home/home.html', controller: 'moHome' },
        'footer': { templateUrl: 'partials/common/footer-login.html', controller: 'moHome' }
      }
    })
    .state('medarbejder', {
      url: "/medarbejder",
      abstract : true,
      authenticate : true,
      data:{
        page: {"translation": true, "key": "employee", "subKey": "", "title": ""}
      },
      views: { 
        'header': { templateUrl: 'partials/common/header.html', controller: 'moHeader' },
        'main': { templateUrl: 'partials/employee/employee.html', controller: 'moEmployee' },
        'orgTree': { templateUrl: 'partials/common/orgTree.html', controller: 'moOrgTree' },
        'notification': { templateUrl: 'partials/common/notification.html', controller: 'moNotification' },
        'footer': { templateUrl: 'partials/common/footer.html', controller: 'moHome' }
      }
    })
    .state('medarbejder.search', {
      url: "?query",
      authenticate : true,
      data:{
        page: {"translation": true, "key": "employee", "subKey": "", "title": ""}
      },
      views: { 
        'header': { templateUrl: 'partials/common/header.html', controller: 'moHeader' },
        'main': { templateUrl: 'partials/employee/employeesList.html', controller: 'moEmployeeList' },
        'orgTree': { templateUrl: 'partials/common/orgTree.html', controller: 'moOrgTree' },
        'notification': { templateUrl: 'partials/common/notification.html', controller: 'moNotification' },
        'footer': { templateUrl: 'partials/common/footer.html', controller: 'moHome' }
      }
    })
    .state('medarbejder.list', {
      url: "",
      authenticate : true,
      data:{
        page: {"translation": true, "key": "employee", "subKey": "", "title": ""}
      },
      views: { 
        'header': { templateUrl: 'partials/common/header.html', controller: 'moHeader' },
        'main': { templateUrl: 'partials/employee/employeesList.html', controller: 'moEmployee' },
        'orgTree': { templateUrl: 'partials/common/orgTree.html', controller: 'moOrgTree' },
        'notification': { templateUrl: 'partials/common/notification.html', controller: 'moNotification' },
        'footer': { templateUrl: 'partials/common/footer.html', controller: 'moHome' }
      }
    })
    .state('medarbejder.detail', {
      url: "/:cpr",
      authenticate : true,
      data:{
        page: {"translation": false, "key": "employee", "subKey": "detail", "title": ""}
      },
      views: { 
        'header': { templateUrl: 'partials/common/header.html', controller: 'moHeader' },
        'main': { templateUrl: 'partials/employee/employeeDetails.html', controller: 'moEmployeeDetail' },
        'orgTree': { templateUrl: 'partials/common/orgTree.html', controller: 'moOrgTree' },
        'notification': { templateUrl: 'partials/common/notification.html', controller: 'moNotification' },
        'footer': { templateUrl: 'partials/common/footer.html', controller: 'moHome' }
      }
    })
    .state('timemachine', {
      url: "/timemachine",
      authenticate : true,
      data:{
        page: {"translation": true, "key": "organisation", "subKey": "timemachine", "title": "Time Machine"}
      },
      views: { 
        'header': { templateUrl: 'partials/common/header-timemachine.html'},
        'main': { templateUrl: 'partials/organisation/timemachine.html', controller: 'moTimemachine' },
        'footer': {}
      }
    })
    .state('help', {
      url: "/help",
      authenticate : true,
      data:{
        page: {"translation": true, "key": "organisation", "subKey": "help", "title": ""}
      },
      views: { 
        'header': { templateUrl: 'partials/common/header-help.html'},
        'main': { templateUrl: 'partials/common/help.html', controller: 'moAppHelp' },
        'footer': {}
      }
    })
    //Organisation starts
    .state('organisation', {
      url: "/organisation",
      abstract : true,
      authenticate : true,
      data:{
        page: {"translation": true, "key": "organisation", "subKey": "", "title": ""}
      },
      views: { 
        'header': { templateUrl: 'partials/common/header.html', controller: 'moHeader' },
        'main': { templateUrl: 'partials/organisation/organisation.html', controller: 'moOrganisation' },
        'orgTree': { templateUrl: 'partials/common/orgTree.html', controller: 'moOrgTree' },
        'notification': { templateUrl: 'partials/common/notification.html', controller: 'moNotification' },
        'footer': { templateUrl: 'partials/common/footer.html', controller: 'moHome' }
      }
    })
    .state('organisation.search', {
      url: "?query",
      authenticate : true,
      data:{
        page: {"translation": true, "key": "organisation", "subKey": "", "title": ""}
      },
      views: { 
        'header': { templateUrl: 'partials/common/header.html', controller: 'moHeader' },
        'main': { templateUrl: 'partials/organisation/organisationsList.html', controller: 'moOrganisationList' },
        'orgTree': { templateUrl: 'partials/common/orgTree.html', controller: 'moOrgTree' },
        'notification': { templateUrl: 'partials/common/notification.html', controller: 'moNotification' },
        'footer': { templateUrl: 'partials/common/footer.html', controller: 'moHome' }
      }
    })
    .state('organisation.list', {
      url: "",
      authenticate : true,
      data:{
        page: {"translation": true, "key": "organisation", "subKey": "", "title": ""}
      },
      views: { 
        'header': { templateUrl: 'partials/common/header.html', controller: 'moHeader' },
        'main': { templateUrl: 'partials/organisation/organisationsList.html', controller: 'moOrganisation' },
        'orgTree': { templateUrl: 'partials/common/orgTree.html', controller: 'moOrgTree' },
        'notification': { templateUrl: 'partials/common/notification.html', controller: 'moNotification' },
        'footer': { templateUrl: 'partials/common/footer.html', controller: 'moHome' }
      }
    })
    .state('organisation.detail', {
      url: "/:cpr",
      authenticate : true,
      data:{
        page: {"translation": false, "key": "organisation", "subKey": "detail", "title": ""}
      },
      views: { 
        'header': { templateUrl: 'partials/common/header.html', controller: 'moHeader' },
        'main': { templateUrl: 'partials/organisation/organisationDetails.html', controller: 'moOrganisationDetail' },
        'orgTree': { templateUrl: 'partials/common/orgTree.html', controller: 'moOrgTree' },
        'notification': { templateUrl: 'partials/common/notification.html', controller: 'moNotification' },
        'footer': { templateUrl: 'partials/common/footer.html', controller: 'moHome' }
      }
    })
    .state('organisation.detail.date', {
      url: "/:date",
      authenticate : true,
      data:{
        page: {"translation": false, "key": "organisation", "subKey": "detail", "title": ""}
      },
      views: { 
        'header': { templateUrl: 'partials/common/header.html', controller: 'moHeader' },
        'main': { templateUrl: 'partials/organisation/organisationDetails.html', controller: 'moOrganisationDetail' },
        'orgTree': { templateUrl: 'partials/common/orgTree.html', controller: 'moOrgTree' },
        'notification': { templateUrl: 'partials/common/notification.html', controller: 'moNotification' },
        'footer': { templateUrl: 'partials/common/footer.html', controller: 'moHome' }
      }
    });
    $urlRouterProvider.otherwise("/");
    datepickerPopupConfig.dateFormat = "dd-MM-yyyy";
    datepickerPopupConfig.datepickerPopup = "dd-MM-yyyy";
    cfpLoadingBarProvider.includeSpinner = true;
    $httpProvider.interceptors.push('tokenInjector');
    $httpProvider.interceptors.push('myHttpInterceptor');
    hotkeysProvider.includeCheatSheet = true;
  }]).run(function ($rootScope, $state, sysAuth, editableOptions, editableThemes) {
    editableOptions.theme = 'bs3'; // bootstrap3 theme. Can be also 'bs2', 'default'
    editableThemes.bs3.inputClass = 'input-sm';
    editableThemes.bs3.buttonsClass = 'btn-sm';
    $rootScope.$on("$stateChangeStart", function(event, toState, toParams, fromState, fromParams){
      //$rootScope.$state = toState;
      //$rootScope.page = toState.data.page;
      $rootScope.authenticate=toState.authenticate;
      if(!sysAuth.getUserAuthentication()){
        if (toState.authenticate){
          // User isn’t authenticated
          $state.transitionTo("home");
          event.preventDefault(); 
        }
      }
    });
  });