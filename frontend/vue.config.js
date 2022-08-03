// SPDX-FileCopyrightText: 2018-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

const webpack = require("webpack")
const BundleAnalyzerPlugin = require("webpack-bundle-analyzer").BundleAnalyzerPlugin

// Names of folders in "./src/modules/"
// This duplicates the contents of "./moduleNames.js" (which is an ES6 module
// that cannot be imported here.)
const _moduleNames = ["organisationMapper", "query", "insight"]

module.exports = {
  assetsDir: "static",
  lintOnSave: true,
  runtimeCompiler: true, // allows the template option in components
  chainWebpack: (config) => {
    // disable eslinting for now...
    config.module.rules.delete("eslint")
  },
  configureWebpack: {
    plugins: [
      new webpack.HashedModuleIdsPlugin(), // so that file hashes don't change unexpectedly
      new webpack.IgnorePlugin(/^\.\/locale$/, /moment$/), // ignore locales and import in main.js instead
      new webpack.DefinePlugin({
        MODULES: JSON.stringify(_moduleNames),
      }),
      new BundleAnalyzerPlugin({
        analyzerMode: "static",
        openAnalyzer: false,
      }),
    ],
    optimization: {
      splitChunks: {
        chunks: "all",
        minSize: 10000,
        maxSize: 250000,
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            reuseExistingChunk: true,
          },
        },
      },
    },
    stats: "errors-warnings",
  },
  transpileDependencies: [/\bvue-awesome\b/],
  pluginOptions: {
    i18n: {
      // Specifies the default locale for vue-i18n
      locale: "da",
      // Specifies the default fallback locale for vue-i18n
      fallbackLocale: "da",
      localeDir: "i18n",
      enableInSFC: false,
    },
  },
  devServer: {
    disableHostCheck: true,
    progress: false,
    port: 80,
  },
}
