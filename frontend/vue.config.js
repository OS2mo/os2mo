const webpack = require('webpack')

module.exports = {
  lintOnSave: true,
  configureWebpack: {
    plugins: [
      new webpack.HashedModuleIdsPlugin() // so that file hashes don't change unexpectedly
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
      }
    }
  }
}
