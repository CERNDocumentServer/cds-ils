import React from 'react';
import { Route } from 'react-router-dom';
import { Importer } from '../backoffice/Importer';
import { CdsBackOfficeRoutes } from './BackofficeUrls';

export const ImporterRoute = () => {
  return (
    <Route exact path={CdsBackOfficeRoutes.importer} component={Importer} />
  );
};
