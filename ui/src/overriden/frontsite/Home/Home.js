import {
  documentApi,
  DocumentCardGroup,
  FrontSiteRoutes,
} from '@inveniosoftware/react-invenio-app-ils';
import React from 'react';
import { Container } from 'semantic-ui-react';

export const Home = () => {
  return (
    <Container fluid className="fs-landing-page-section-wrapper">
      <Container fluid className="dot-background-container">
        <Container fluid className="dot-background">
          <Container
            textAlign="center"
            className="fs-landing-page-section no-background"
          >
            <DocumentCardGroup
              title="Most Loaned Books"
              headerClass="section-header highlight"
              fetchDataMethod={documentApi.list}
              fetchDataQuery={documentApi
                .query()
                .withDocumentType('BOOK')
                .sortBy('-mostloaned')
                .withSize(5)
                .qs()}
              viewAllUrl={FrontSiteRoutes.documentsListWithQuery(
                '&sort=mostloaned&order=desc'
              )}
            />
          </Container>
        </Container>
      </Container>
      <Container textAlign="center" className="fs-landing-page-section">
        <DocumentCardGroup
          title="Most Recent Books"
          headerClass="section-header highlight"
          fetchDataMethod={documentApi.list}
          fetchDataQuery={documentApi
            .query()
            .withDocumentType('BOOK')
            .sortBy('mostrecent')
            .withSize(5)
            .qs()}
          viewAllUrl={FrontSiteRoutes.documentsListWithQuery(
            '&sort=mostrecent&order=desc'
          )}
        />
      </Container>
      <Container textAlign="center" className="fs-landing-page-section">
        <DocumentCardGroup
          title="Most Recent E-Books"
          headerClass="section-header highlight"
          fetchDataMethod={documentApi.list}
          fetchDataQuery={documentApi
            .query()
            .withDocumentType('BOOK')
            .withEitems()
            .sortBy('-mostrecent')
            .withSize(5)
            .qs()}
          viewAllUrl={FrontSiteRoutes.documentsListWithQuery(
            '&f=doctype%3ABOOK&f=medium%3AELECTRONIC_VERSION&sort=mostrecent&order=desc'
          )}
        />
      </Container>
    </Container>
  );
};
