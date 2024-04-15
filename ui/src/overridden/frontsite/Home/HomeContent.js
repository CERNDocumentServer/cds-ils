import {
  documentApi,
  DocumentCardGroup,
  SeriesCardGroup,
  FrontSiteRoutes,
  Headline,
  seriesApi,
} from "@inveniosoftware/react-invenio-app-ils";
import React from "react";
import { parametrize } from "react-overridable";
import {
  Button,
  Container,
  Divider,
  Grid,
  Message,
  Header,
  Icon,
  List,
} from "semantic-ui-react";
import { Link as ScrollLink } from "react-scroll";
import { snvLink } from "../../utils";

export const HomeHeadline = parametrize(Headline, {
  backgroundImageURL: process.env.PUBLIC_URL + "/images/home-headline-background.jpg",
});

export const HomeButtons = () => {
  return (
    <Container className="container-extra">
      <Divider />
      <Grid>
        <Grid.Column width={16} textAlign="center">
          <Button
            className="headline-quick-access"
            as={ScrollLink}
            to="recent-books"
            offset={-100}
            smooth
            primary
          >
            <Icon name="book" />
            Recent books
          </Button>
          <Button
            className="headline-quick-access"
            as={ScrollLink}
            to="recent-journals"
            offset={-100}
            smooth
            primary
          >
            <Icon name="file alternate" />
            Recent journals
          </Button>
          <Button
            className="headline-quick-access"
            as={ScrollLink}
            to="most-loaned"
            offset={-100}
            smooth
            primary
          >
            <Icon name="star" />
            Most loaned
          </Button>
          <Button
            className="headline-quick-access"
            as={ScrollLink}
            to="standards"
            offset={-100}
            smooth
            primary
          >
            <Icon name="chart pie" />
            Standards
          </Button>
        </Grid.Column>
      </Grid>
    </Container>
  );
};

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
              title="Recent books and e-books"
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
        id="recent-journals"
      >
        <SeriesCardGroup
          title="Recent journals and e-journals"
          headerClass="section-header highlight"
          fetchDataMethod={seriesApi.list}
          fetchDataQuery={seriesApi
            .query()
            .withSeriesType("PERIODICAL")
            .sortBy("-created")
            .withSize(5)
            .qs()}
          viewAllUrl={FrontSiteRoutes.documentsListWithQuery(
            "&f=doctype%3APERIODICAL&sort=created&order=desc"
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
      <Container textAlign="center" className="fs-landing-page-section" id="standards">
        <Header as="h2" className="section-header highlight">
          Current and historical standards
        </Header>
        <Message info icon style={{ justifyContent: "center" }}>
          <Icon name="info circle" />
          <List className="mt-5">
            <Message.Header>
              CERN readers have access to {snvLink} and can search directly!
            </Message.Header>
            <Message.Content>
              CERN readers can access the standards online and download them on their
              computers as PDF files.
            </Message.Content>
          </List>
        </Message>
      </Container>
    </Container>
  );
};
