import { InvenioILSApp } from '@inveniosoftware/react-invenio-app-ils';
import React from 'react';
import 'react-app-polyfill/ie11'; // For IE 11 support
import ReactDOM from 'react-dom';
import { OverridableContext } from 'react-overridable';
import 'semantic-ui-less/semantic.less';
import { config } from './config';

const CustomHome = ({ ...props }) => {
  return <>CERN Library Catalogue</>;
};

const overriddenCmps = {
  // 'Home.layout': CustomHome,
};

ReactDOM.render(
  <OverridableContext.Provider value={overriddenCmps}>
    <InvenioILSApp config={config} />
  </OverridableContext.Provider>,
  document.getElementById('app')
);
