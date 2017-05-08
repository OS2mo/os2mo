'use strict';

/* Filters */

angular.module('moApp.filters', []).
	filter('toArray', function () {
		return function (obj) {
			if (!(obj instanceof Object)) {
				return obj;
			}

		return Object.keys(obj).map(function (key) {
			return Object.defineProperty(obj[key], '$key', {__proto__: null, value: key});
		});
		}
	})
	.filter("fullDate", function ($filter) {
 		return function(input)
 		{
			if(input instanceof Date){ return input; }
	        var parts = input.split("-");
	        var dt = new Date();
	        dt.setDate(parseInt(parts[0]));
	        dt.setMonth(parseInt(parts[1]));
	        dt.setYear(parseInt(parts[2]));
	        dt.setDate(dt.getDate()-1);

	        return dt;
  			/*if(input == 'infinity'){ return ""; } 
  			if(input == '-infinity'){ return ""; } 
  			input = new Date();
  			return input;*/
		};
	})
	.filter('unsafe', ['$sce', function ($sce) {
	    return function (val) {
	        return $sce.trustAsHtml(val);
	    };
	}]);
