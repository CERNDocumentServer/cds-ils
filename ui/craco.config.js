var path = require('path');

module.exports = {
  plugins: [{ plugin: require('@semantic-ui-react/craco-less') }],
  eslint: {
    enable: true /* (default value) */,
    useEslintrc: true,
    mode: 'file',
  },
  webpack: {
    alias: {
      // react-searchkit peer dependencies, to avoid duplication
      axios: path.resolve('./node_modules/axios'),
      formik: path.resolve('./node_modules/formik'),
      lodash: path.resolve('./node_modules/lodash'),
      luxon: path.resolve('./node_modules/luxon'),
      'prop-types': path.resolve('./node_modules/prop-types'),
      qs: path.resolve('./node_modules/qs'),
      react: path.resolve('./node_modules/react'),
      'react-dom': path.resolve('./node_modules/react-dom'),
      'react-router-dom': path.resolve('./node_modules/react-dom'),
      'react-overridable': path.resolve('./node_modules/react-overridable'),
      'react-searchkit': path.resolve('./node_modules/react-searchkit'),
      'react-redux': path.resolve('./node_modules/react-redux'),
      redux: path.resolve('./node_modules/redux'),
      'redux-thunk': path.resolve('./node_modules/redux-thunk'),
      yup: path.resolve('./node_modules/yup'),
    },
  }
};
