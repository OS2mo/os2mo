module.exports = function(grunt) {
  require('matchdep').filterDev('grunt-*').forEach(grunt.loadNpmTasks);
  // Project configuration.
  grunt.initConfig({
    bower: grunt.file.readJSON('./.bowerrc'),
    pkg: grunt.file.readJSON('./package.json'),
    uglify: {
      dev:{
          options: {
            banner: '/*! <%= pkg.name %> lib - v<%= pkg.version %> -' +
                    '<%= grunt.template.today("yyyy-mm-dd HH:mm") %> */',
            separator: ';'
          },
          dest: '<%= pkg.dev %>/scripts/core.js',
          src: [
            //'bower_components/jquery/dist/jquery.js',
            'bower_components/angular/angular.js',
            'bower_components/angular-animate/angular-animate.js',
            //'bower_components/angular-mocks/angular-mocks.js',
            'bower_components/angular-route/angular-route.js',
            'bower_components/angular-cookies/angular-cookies.js',
            'bower_components/angular-ui-router/release/angular-ui-router.js',
            'bower_components/underscore/underscore.js',
            //'bower_components/bootstrap/dist/js/bootstrap.min.js',
            'bower_components/angular-bootstrap/ui-bootstrap.js',
            'bower_components/angular-bootstrap/ui-bootstrap-tpls.js',
            'bower_components/ng-table/ng-table.min.js',
            'bower_components/angular-xeditable/dist/js/xeditable.js',
            'bower_components/angular-loading-bar/src/loading-bar.js',
            'bower_components/angular-bindonce/bindonce.js',
            //'bower_components/spin.js/dist/spin.js',
            //'bower_components/angular-spinner/angular-spinner.js',
            'bower_components/angular-hotkeys/build/hotkeys.js',
            'bower_components/angular-ui-utils/modules/keypress/keypress.js',
            'bower_components/angular-tree-control/angular-tree-control.js',
            'bower_components/angular-local-storage/dist/angular-local-storage.js',
            '<%= pkg.dev %>/scripts/thirdparty/angular.tree.js'
            ]
      },
      prod:{
          options: {
            banner: '/*! <%= pkg.name %> lib - v<%= pkg.version %> -' +
                    '<%= grunt.template.today("yyyy-mm-dd HH:mm") %> */',
            separator: ';'
          },
          dest: '<%= pkg.dist %>/assets/scripts/core.js',
          src: [
            '<%= bower.directory %>/jquery/dist/jquery.js',
            '<%= bower.directory %>/angular/angular.min.js',
            '<%= bower.directory %>/angular-animate/angular-animate.js',
            '<%= bower.directory %>/angular-mocks/angular-mocks.js',
            '<%= bower.directory %>/angular-route/angular-route.js',
            '<%= bower.directory %>/bootstrap/dist/js/bootstrap.min.js'
            ]
      }
    },
    less: {
      dev: {
        options: {
          paths: ["<%= pkg.dev %>/styles/"]
        },
        files: {
          "<%= pkg.dev %>/styles/core.css": "bower_components/bootstrap/less/bootstrap.less",
          "<%= pkg.dev %>/styles/custom.css": "<%= pkg.dev %>/styles/app/custom.less"
        }
      },
      prod: {
        options: {
          paths: ["<%= pkg.dist %>/assets/styles/"],
          cleancss: true
        },
        files: {
          "<%= pkg.dist %>/assets/styles/core.css": "<%= bower.directory %>/bootstrap/less/bootstrap.less"
        }
      }
    },
    concat: {
      css: {
        options: {
        },
        src: [
          '<%= pkg.dev %>/styles/core.css',
          'bower_components/angular-xeditable/dist/css/xeditable.css',
          'bower_components/angular-loading-bar/src/loading-bar.css',
          'bower_components/ng-table/ng-table.min.css',
          'bower_components/angular-hotkeys/build/hotkeys.min.css',
          'bower_components/angular-tree-control/css/tree-control.css',
          'bower_components/angular-tree-control/css/tree-control-attribute.css'
        ],
        dest: '<%= pkg.dev %>/styles/core.css'
      }
    },
    cssmin: {
      dev: {
        options: {
          expand: true,
          banner: '/*! <%= pkg.name %> - v<%= pkg.version %> - ' +
          '<%= grunt.template.today("yyyy-mm-dd") %> */'
        },
        files: {
          '<%= pkg.dev %>/styles/core.min.css': ['<%= pkg.dev %>/styles/core.css'],
          '<%= pkg.dev %>/styles/custom.min.css': ['<%= pkg.dev %>/styles/custom.css']
        }
      }
    },
    copy: {
      dev: {
        files: [
          {expand: true, flatten: true, src: ['bower_components/bootstrap/dist/fonts/*'], dest: '<%= pkg.dev %>/fonts/', filter: 'isFile'}
        ]
      },
      prod: {
        files: [
          {expand: true, flatten: true, src: ['<%= bower.directory %>/bootstrap/dist/fonts/*'], dest: '<%= pkg.dist %>/assets/fonts/', filter: 'isFile'},
          // Copy app js to prod
          {expand: true, flatten: true, src: ['<%= pkg.dev %>/assets/scripts/app/*'], dest: '<%= pkg.dist %>/assets/scripts/app/', filter: 'isFile'},
          // Copy images from dev to prod
          {expand: true, flatten: true, src: ['<%= pkg.dev %>/assets/images/*'], dest: '<%= pkg.dist %>/assets/images/', filter: 'isFile'},
          // Copy app.css to prod
          {expand: true, flatten: true, src: ['<%= pkg.dev %>/assets/styles/app.css'], dest: '<%= pkg.dist %>/assets/styles/', filter: 'isFile'},
          // Copy app.js to prod
          {expand: true, flatten: true, src: ['<%= pkg.dev %>/assets/scripts/app.js'], dest: '<%= pkg.dist %>/assets/scripts/', filter: 'isFile'},
        ]
      }
    },
    watch: {
      less: {
        files: [
          '<%= pkg.dev %>/styles/app/*.less'
        ],
        tasks: ['cssmin', 'less']
      }
    },
    karma: {
      unit: {
          configFile: 'config/karma.conf.js'
      }
    },
    bower: {
      install: {
        options: {
          targetDir: './bower_components',
          layout: 'byComponent',
          copy: false,
          install: true,
          bowerOptions: {}
        }
      }
    }
  });

  grunt.registerTask('default', ['dev']);
  //grunt.registerTask('all', ['dev','prod']);
  grunt.registerTask('dev', ['bower', 'uglify:dev', 'copy:dev', 'less:dev', 'concat:css', 'cssmin:dev']);//, 'watch:assets']);
  grunt.registerTask('test', ['bower', 'uglify:dev', 'copy:dev', 'less:dev', 'concat:css', 'cssmin:dev', 'karma']);//, 'watch:assets']);
  grunt.registerTask('watch', ['live']);
  //grunt.registerTask('prod', ['uglify:prod', 'copy:prod', 'less:prod']);//, 'watch:assets']);
  //grunt.registerTask('prod', ['min:prod']);
};
