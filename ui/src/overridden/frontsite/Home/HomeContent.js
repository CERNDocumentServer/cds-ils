import {
  documentApi,
  DocumentCardGroup,
  FrontSiteRoutes,
  Headline,
} from "@inveniosoftware/react-invenio-app-ils";
import React from "react";
import { parametrize } from "react-overridable";
import { Container } from "semantic-ui-react";

export const HomeHeadline = parametrize(Headline, {
  backgroundImageURL: process.env.PUBLIC_URL + "/images/home-headline-background.jpg",
});

export const HomeContent = () => {
  return (
    <Container fluid className="fs-landing-page-section-wrapper">
      <Container fluid className="dot-background-container">
        <Container fluid className="dot-background">
          <Container
            textAlign="center"
            className="fs-landing-page-section no-background"
            id="recent-books"
          >
            <DocumentCardGroup
              title="Most recent books"
              headerClass="section-header highlight"
              fetchDataMethod={documentApi.list}
              fetchDataQuery={documentApi
                .query()
                .withDocumentType("BOOK")
                .sortBy("-created")
                .withSize(5)
                .qs()}
              viewAllUrl={FrontSiteRoutes.documentsListWithQuery(
                "&sort=created&order=desc"
              )}
            />
          </Container>
        </Container>
      </Container>
      <Container
        textAlign="center"
        className="fs-landing-page-section"
        id="recent-ebooks"
      >
        <DocumentCardGroup
          title="Most recent e-books"
          headerClass="section-header highlight"
          fetchDataMethod={documentApi.list}
          fetchDataQuery={documentApi
            .query()
            .withDocumentType("BOOK")
            .withEitems()
            .sortBy("-created")
            .withSize(5)
            .qs()}
          viewAllUrl={FrontSiteRoutes.documentsListWithQuery(
            "&f=doctype%3ABOOK&f=medium%3AE-BOOK&sort=created&order=desc"
          )}
        />
      </Container>
      <Container
        textAlign="center"
        className="fs-landing-page-section"
        id="most-loaned"
      >
        <DocumentCardGroup
          title="Most loaned books"
          headerClass="section-header highlight"
          fetchDataMethod={documentApi.list}
          fetchDataQuery={documentApi
            .query()
            .withDocumentType("BOOK")
            .sortBy("-mostloaned")
            .withSize(5)
            .qs()}
          viewAllUrl={FrontSiteRoutes.documentsListWithQuery(
            "&sort=mostloaned&order=desc"
          )}
        />
      </Container>
    </Container>
  );
};
