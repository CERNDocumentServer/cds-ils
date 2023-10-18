var path = require('path');

module.exports = {
  plugins: [{ plugin: require('@semantic-ui-react/craco-less') }],
  eslint: {
    enable: true /* (default value) */,
    useEslintrc: true,
    mode: 'file',
  },
  webpack: {
    configure: webpackConfig => {
      const scopePluginIndex = webpackConfig.resolve.plugins.findIndex(
        ({ constructor }) => constructor && constructor.name === 'ModuleScopePlugin'  // Needed to skip the check of preventing from importing from outside of src/ and node_modules/ directory.
      );

      webpackConfig.resolve.plugins.splice(scopePluginIndex, 1);
      return webpackConfig;
    },
    alias: {
      // aliases for all peer dependencies to avoid double libraries
      '@babel/runtime': path.resolve('./node_modules/@babel/runtime'),
      axios: path.resolve('./node_modules/axios'),
      formik: path.resolve('./node_modules/formik'),
      less: path.resolve('./node_modules/less'),
      'less-loader': path.resolve('./node_modules/less-loader'),
      lodash: path.resolve('./node_modules/lodash'),
      luxon: path.resolve('./node_modules/luxon'),
      path: path.resolve('./node_modules/path'),
      'prop-types': path.resolve('./node_modules/prop-types'),
      qs: path.resolve('./node_modules/qs'),
      react: path.resolve('./node_modules/react'),
      'react-app-polyfill': path.resolve('./node_modules/react-app-polyfill'),
      'react-copy-to-clipboard': path.resolve(
        './node_modules/react-copy-to-clipboard'
      ),
      'react-dom': path.resolve('./node_modules/react-dom'),
      'react-overridable': path.resolve('./node_modules/react-overridable'),
      'react-redux': path.resolve('./node_modules/react-redux'),
      'react-router-dom': path.resolve('./node_modules/react-router-dom'),
      'react-scroll': path.resolve('./node_modules/react-scroll'),
      'react-searchkit': path.resolve('./node_modules/react-searchkit'),
      'react-show-more': path.resolve('./node_modules/react-show-more'),
      'react-tagcloud': path.resolve('./node_modules/react-tagcloud'),
      redux: path.resolve('./node_modules/redux'),
      'redux-devtools-extension': path.resolve(
        './node_modules/redux-devtools-extension'
      ),
      'redux-thunk': path.resolve('./node_modules/redux-thunk'),
      'semantic-ui-calendar-react': path.resolve(
        './node_modules/semantic-ui-calendar-react'
      ),
      'semantic-ui-less': path.resolve('./node_modules/semantic-ui-less'),
      'semantic-ui-react': path.resolve('./node_modules/semantic-ui-react'),
      yup: path.resolve('./node_modules/yup'),
    },
  },
};
