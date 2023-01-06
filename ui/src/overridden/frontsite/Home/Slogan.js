import React from "react";
import { Container, Grid, Header } from "semantic-ui-react";

export const Slogan = ({ ...props }) => {
  return (
    <Container className="container-header">
      <Grid>
        <Grid.Column width={16} textAlign="left">
          <Header as="h1" className="fs-headline-header" size="huge">
            CERN Library Catalogue
          </Header>
          <Header.Subheader className="fs-headline-subheader">
            Books, e-books, journals, standards at CERN.
          </Header.Subheader>
        </Grid.Column>
      </Grid>
    </Container>
  );
};
