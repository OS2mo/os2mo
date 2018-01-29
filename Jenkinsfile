// -*- groovy -*-

pipeline {
  agent any

  environment {
    MINIMOX_DIR = '/srv/minimox'
    BROWSER = 'Firefox'
  }

  stages {
    stage('Build') {
      steps {
        echo 'Building...'

        timeout(5) {
          sh './build/run-build.sh'
        }
      }
    }

    stage('Test') {
      steps {
        echo 'Testing..'

        timeout(5) {
          sh './build/run-tests.sh'
        }
      }
    }

    stage('Deploy') {
      steps {
        echo 'Deploying....'

        timeout(5) {
          sh './build/run-deploy.sh'
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
