import React from "react";
import { Grid, Embed, Button, Icon, Message, List } from "semantic-ui-react";
import PropTypes from "prop-types";
import _isEmpty from "lodash/isEmpty";
import { shelfLink } from "../../utils";

export const ItemCirculationShelf = ({ metadata }) => {
  return !_isEmpty(metadata.shelf) ? (
    <Grid.Column width={6}>
      <>
        <Embed active url={shelfLink(metadata.shelf, true)} />
        <Button
          as="a"
          smooth
          href={shelfLink(metadata.shelf)}
          target="_blank"
          rel="noreferrer"
          color="blue"
          fluid
        >
          <Icon name="map pin" />
          SHELF {metadata.shelf}
        </Button>
      </>
    </Grid.Column>
  ) : (
    <Grid.Column width={6}>
      <Message warning icon style={{ justifyContent: "center" }}>
        <Icon name="exclamation circle" />
        <List className="mt-5">
          <Message.Header>Shelf location missing!</Message.Header>
        </List>
      </Message>
    </Grid.Column>
  );
};

ItemCirculationShelf.propTypes = {
  metadata: PropTypes.object.isRequired,
};
