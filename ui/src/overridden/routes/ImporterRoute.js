import React from 'react';
import { Importer } from '../backoffice/Importer';
import { CdsBackOfficeRoutes } from './BackofficeUrls';
import { Switch, Route } from 'react-router-dom';
import { NotFound } from '@inveniosoftware/react-invenio-app-ils';

export const ImporterRoute = () => {
  return (
    <>
      <Route exact path={CdsBackOfficeRoutes.importer} component={Importer} />
      <Route>
        <NotFound />
      </Route>
    </>
  );
};
