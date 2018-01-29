// -*- groovy -*-

pipeline {
  agent any

  environment {
    MINIMOX_DIR = '/srv/minimox'
  }

  stages {
    stage('Build') {
      steps {
        echo 'Building...'

        sh './manage.py build'
        sh './manage.py sphinx'
        sh './manage.py python -- -m pip install -r requirements-test.txt'
      }
    }

    stage('Test') {
      steps {
        echo 'Testing..'

        sh 'mkdir -p build/coverage build/reports'
        sh 'yarn unit'
        sh './manage.py python -- -m pytest --verbose --cov=mora --cov-report=xml:build/coverage/python.xml --cov-config=.coveragerc --junitxml=build/reports/python.xml tests mora'
      }
    }

    stage('Deploy') {
      steps {
        echo 'Deploying....'
      }
    }
  }

  post {
        always {
            junit 'build/reports/*.xml'
            step([
                 $class: 'CoberturaPublisher',
                 autoUpdateHealth: true,
                 autoUpdateStability: true,
                 coberturaReportFile: 'build/coverage/*.xml',
                 failUnhealthy: true,
                 failUnstable: true,
                 maxNumberOfBuilds: 0,
                 onlyStable: false,
                 sourceEncoding: 'ASCII',
                 zoomCoverageChart: true,
                 ])
        }
    }
}
