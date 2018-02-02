// -*- groovy -*-

pipeline {
  agent any

  environment {
    MINIMOX_DIR = '/srv/minimox'
    BROWSER = 'Firefox'
    MOZ_HEADLESS = '1'
    PYTEST_ADDOPTS = '--color=yes'
  }

  stages {
    stage('Fetch') {
      steps {
        timeout(2) {
          ansiColor('xterm') {
            sh './build/run-fetch.sh'
          }
        }
      }
    }

    stage('Check') {
      steps {
        timeout(2) {
          ansiColor('xterm') {
            sh './build/run-check.sh'
          }
        }
      }
    }

    stage('Build') {
      steps {
        echo 'Building...'

        timeout(10) {
          ansiColor('xterm') {
            sh './build/run-build.sh'
          }
        }
      }
    }

    stage('Test') {
      steps {
        echo 'Testing..'

        timeout(10) {
          ansiColor('xterm') {
            sh './build/run-tests.sh'
          }
        }
      }
    }

    stage('Deploy') {
      steps {
        echo 'Deploying....'

        timeout(1) {
          ansiColor('xterm') {
            sh './build/run-deploy.sh'
          }
        }
      }
    }
  }

  post {
    always {
      junit healthScaleFactor: 200.0,           \
        testResults: 'build/reports/*.xml'

      warnings canRunOnFailed: true, consoleParsers: [
        [parserName: 'Sphinx-build'],
        [parserName: 'Pep8']
      ]

      cobertura coberturaReportFile: 'build/coverage/*.xml',    \
        conditionalCoverageTargets: '90, 0, 0',                 \
        lineCoverageTargets: '95, 0, 0',                        \
        maxNumberOfBuilds: 0
    }
  }
}
