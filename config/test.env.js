'use strict'
const merge = require('webpack-merge')
const devEnv = require('./dev.env')

module.exports = merge(devEnv, {
  NODE_ENV: '"testing"',
  USERSNAP_KEY: '"0679ace2-8ba0-4e07-81a3-fc50d0eb1dea"'
})
