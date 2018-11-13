module.exports = {
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
      "/service": {
        target: process.env.BASE_URL || "http://localhost:5000/",
        changeOrigin: true
      },
      "/saml": {
        target: process.env.BASE_URL || "http://localhost:5000/",
        changeOrigin: true
      }
    }
  }
}
