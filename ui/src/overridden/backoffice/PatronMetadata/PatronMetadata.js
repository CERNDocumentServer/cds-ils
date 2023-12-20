import {
  MetadataTable,
  ScrollingMenuItem,
} from "@inveniosoftware/react-invenio-app-ils";
import PropTypes from "prop-types";
import React from "react";
import { Grid, Header, Segment } from "semantic-ui-react";
import { config } from "../../../config";

export const PatronMetadata = ({ patron, ...props }) => {
  const leftTable = [
    { name: "Name", value: patron.metadata.name },
    { name: "Email", value: patron.metadata.email },
    { name: "Mailbox", value: patron.metadata.mailbox },
  ];
  const rightTable = [
    { name: "Person ID", value: patron.metadata.person_id },
    { name: "Department", value: patron.metadata.department },
    {
      name: "CERN Profile",
      value: patron.metadata.person_id ? (
        <a
          target="_blank"
          rel="noopener noreferrer"
          href={config.PATRONS.phonebookURLPrefix + patron.metadata.email}
        >
          Phonebook
        </a>
      ) : null,
    },
  ];
  return (
    <>
      <Header attached="top" as="h3">
        Patron metadata
      </Header>
      <Segment attached className="bo-metadata-segment" id="patron-metadata">
        <Grid columns={2}>
          <Grid.Row>
            <Grid.Column>
              <MetadataTable labelWidth={5} rows={leftTable} />
            </Grid.Column>
            <Grid.Column>
              <MetadataTable labelWidth={5} rows={rightTable} />
            </Grid.Column>
          </Grid.Row>
        </Grid>
      </Segment>
    </>
  );
};

export const PatronMetadataActionMenuItem = ({ ...props }) => (
  <ScrollingMenuItem label="Patron metadata" elementId="patron-metadata" />
);

PatronMetadata.propTypes = {
  patron: PropTypes.object.isRequired,
};
