// SPDX-FileCopyrightText: 2018-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

const fs = require('fs')
const webpack = require('webpack')
const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin
const AVAILABLE_MODULES = fs.readdirSync('./src/modules').filter(fn => fn.indexOf('.') === -1)
const MODULES = process.env.MODULES ? process.env.MODULES.split(',') : AVAILABLE_MODULES

MODULES.sort()

module.exports = {
  assetsDir: 'static',
  lintOnSave: true,
  runtimeCompiler: true, // allows the template option in components
  chainWebpack: config => {
    // disable eslinting for now...
    config.module.rules.delete('eslint')
  },
  configureWebpack: {
    plugins: [
      new webpack.HashedModuleIdsPlugin(), // so that file hashes don't change unexpectedly
      new webpack.IgnorePlugin(/^\.\/locale$/, /moment$/), // ignore locales and import in main.js instead
      new webpack.DefinePlugin({
        MODULES: JSON.stringify(MODULES),
      }),
      new BundleAnalyzerPlugin({
        analyzerMode: 'static',
        openAnalyzer: false
      })
    ],
    optimization: {
      splitChunks: {
        chunks: 'all',
        minSize: 10000,
        maxSize: 250000,
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            reuseExistingChunk: true
          }
        }
      }
    }
  },
  transpileDependencies: [
    /\bvue-awesome\b/
  ],
  pluginOptions: {
    i18n: {
      locale: 'da',
      fallbackLocale: 'da',
      localeDir: 'i18n',
      enableInSFC: false
    }
  },
  devServer: {
    proxy: {
      '/service': {
        target: process.env.BASE_URL || 'http://localhost:5000/',
        changeOrigin: true
      },
      '/saml': {
        target: process.env.BASE_URL || 'http://localhost:5000/',
        changeOrigin: true
      },
      '/version': {
        target: process.env.BASE_URL || 'http://localhost:5000/',
        changeOrigin: true
      }
    }
  }
}
