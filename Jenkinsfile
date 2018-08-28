// -*- groovy -*-

pipeline {
  agent any

  environment {
    BROWSER = 'chromium:headless'
    PIPENV_VENV_IN_PROJECT = '1'
    NODE_ENV = 'testing'
    PYTEST_ADDOPTS = '--color=yes'
  }

  stages {
    stage('Build Frontend') {
      agent {
        docker { image 'node:latest' }
      }
      steps {
        timeout(5) {
          sh 'yarn && yarn build'
        }
      }
    }

    stage('Create Environment') {
      steps {
        timeout(5) {
          ansiColor('xterm') {
            sh 'pipenv sync --dev'
          }
        }
      }
    }

    stage('Code Checks') {
      steps {
        timeout(1) {
          ansiColor('xterm') {
            sh 'pipenv run flake8 --exit-zero mora tests'
          }
        }
      }
    }

    stage('Run Tests') {
      steps {
        timeout(12) {
          ansiColor('xterm') {
            sh 'pipenv run test'
          }
        }
      }
    }

    stage('Build Docs') {
      steps {
        timeout(1) {
          ansiColor('xterm') {
            sh 'pipenv run sphinx'
          }
        }

        publishHTML target: [
          allowMissing: true, reportDir: 'docs/out',
          reportFiles: 'index.html', reportName: 'Documentation'
        ]
      }
    }

    stage('Deploy') {
      steps {
        timeout(5) {
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

      cleanWs()
    }
  }
}
