import {
  documentApi,
  DocumentCardGroup,
  FrontSiteRoutes,
  Headline,
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
import { snvLink } from "../utils";

export const HomeHeadline = parametrize(Headline, {
  backgroundImageURL: process.env.PUBLIC_URL + "/images/home-headline-background.jpg",
});

export const HomeButtons = () => {
  return (
    <Container className="container-extra">
      <Divider />
      <Grid>
        <Grid.Row>
          <Grid.Column width={16} textAlign="center">
            <Button
              className="headline-quick-access"
              as={ScrollLink}
              to="recent-books-ebooks"
              offset={-100}
              smooth
              primary
            >
              Recent books/e-books
            </Button>
            <Button
              className="headline-quick-access"
              as={ScrollLink}
              to="recent-journals-ejournals"
              offset={-100}
              smooth
              primary
            >
              Recent journals/e-journals
            </Button>
          </Grid.Column>
        </Grid.Row>
        <Grid.Row>
          <Grid.Column width={16} textAlign="center">
            <Button
              className="headline-quick-access"
              as={ScrollLink}
              to="most-loaned"
              offset={-100}
              smooth
              primary
            >
              Most loaned books
            </Button>
            <Button
              className="headline-quick-access"
              as={ScrollLink}
              to="standards"
              offset={-100}
              smooth
              primary
            >
              Current and historical standards
            </Button>
          </Grid.Column>
        </Grid.Row>
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
            id="recent-books-ebooks"
          >
            <DocumentCardGroup
              title="Most recent books and e-books"
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
        id="recent-journals-ejournals"
      >
        <DocumentCardGroup
          title="Most recent journals and e-journals"
          headerClass="section-header highlight"
          fetchDataMethod={documentApi.list}
          fetchDataQuery="publication_info:*&sort=-created&size=5"
          viewAllUrl={FrontSiteRoutes.documentsListWithQuery(
            "publication_info:*&sort=created&order=desc"
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
