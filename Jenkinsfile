// -*- groovy -*-

pipeline {
  agent any

  stages {
    stage('Build') {
      steps {
        echo 'Building...'

        sh './manage.py build'
        sh './manage.py sphinx'
        sh './manage.py -- -m pip install -r requirements-test.txt'
      }
    }

    stage('Test') {
      steps {
        echo 'Testing..'
        sh 'mkdir -p build/coverage build/reports'

        sh 'yarn unit'
        sh 'py.test --verbose --cov=mora --cov-report=xml:build/coverage/python.xml --cov-config=.coveragerc --junitxml=build/reports/python.xml tests mora'
      }
    }

    stage('Deploy') {
      steps {
        echo 'Deploying....'
      }
    }
  }
}
