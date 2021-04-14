import React from 'react';
import { Header } from 'semantic-ui-react';
import { FrontSiteRoutes } from '@inveniosoftware/react-invenio-app-ils';
import { Link } from 'react-router-dom';

export const DocumentRequestFormHeader = () => {
  return (
    <>
      <Header as="h1">Request new document</Header>
      <p>
        Fill in the form below to request to loan, purchase or suggest a new
        document (book, article, standard, etc.) to the Library.
      </p>
      <p>
        You can see all your requests on your{' '}
        <Link to={FrontSiteRoutes.patronProfile}>profile</Link> page.
      </p>
    </>
  );
};
