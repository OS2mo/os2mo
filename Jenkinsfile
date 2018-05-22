// -*- groovy -*-

pipeline {
  agent any

  environment {
    BROWSER = 'Firefox'
    MOZ_HEADLESS = '1'
    PYTEST_ADDOPTS = '--color=yes'
  }

  stages {
    stage('Fetch') {
      steps {
        dir("../mox") {
          git url: 'https://github.com/magenta-aps/mox', branch: 'feature/21379-mora-testsuite'
        }

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

        publishHTML target: [
          allowMissing: true, reportDir: 'docs/out',
          reportFiles: 'index.html', reportName: 'Documentation'
        ]
      }
    }

    stage('Test') {
      steps {
        echo 'Testing..'

        timeout(15) {
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
