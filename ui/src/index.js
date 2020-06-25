import { history, InvenioILSApp } from '@inveniosoftware/react-invenio-app-ils';
import React from 'react';
import 'react-app-polyfill/ie11'; // For IE 11 support
import ReactDOM from 'react-dom';
import { OverridableContext } from 'react-overridable';
import { Router } from 'react-router-dom';
import 'semantic-ui-less/semantic.less';
import { config } from './config';
import { overriddenCmps } from './overridableMapping';

ReactDOM.render(
  <Router history={history}>
    <OverridableContext.Provider value={overriddenCmps}>
      <InvenioILSApp config={config} />
    </OverridableContext.Provider>
  </Router>,
  document.getElementById('app')
);
