import React from "react";
import { Grid, Embed, Button, Icon } from "semantic-ui-react";
import PropTypes from "prop-types";
import { shelfLink } from "../../utils";

export const ItemCirculationShelf = ({ metadata }) => {
  return (
    <Grid.Column width={6}>
      <>
        <Embed
          active
          url={shelfLink(metadata.shelf, true)}
          style={{
            "padding-bottom": "30%",
            "pointer-events": "none",
          }}
        />
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
  );
};

ItemCirculationShelf.propTypes = {
  metadata: PropTypes.object.isRequired,
};
