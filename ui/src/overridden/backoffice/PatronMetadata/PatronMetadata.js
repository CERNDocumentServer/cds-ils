import {
  ScrollingMenuItem,
  MetadataTable,
} from '@inveniosoftware/react-invenio-app-ils';
import PropTypes from 'prop-types';
import React from 'react';
import { Grid, Header, Segment } from 'semantic-ui-react';

export const PatronMetadata = ({ patron, ...props }) => {
  const leftTable = [
    { name: 'Name', value: patron.metadata.name },
    { name: 'Email', value: patron.metadata.email },
  ];
  const rightTable = [
    { name: 'Person ID', value: patron.metadata.person_id },
    { name: 'Department', value: patron.metadata.department },
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
