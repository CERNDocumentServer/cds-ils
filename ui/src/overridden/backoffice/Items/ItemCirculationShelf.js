import _isEmpty from "lodash/isEmpty";
import React from "react";
import { Grid, Icon } from "semantic-ui-react";
import PropTypes from "prop-types";

export const ItemCirculationShelf = ({ metadata }) => {
  let callNumber = {};
  if (!_isEmpty(metadata.identifiers)) {
    callNumber = metadata.identifiers.find(
      (identifier) => identifier.scheme === "CALL_NUMBER"
    );
  }
  return (
    <Grid.Column width={6}>
      <Icon name="map pin" />
      Call number: {!_isEmpty(callNumber) ? callNumber.value : "missing"}
      {metadata.shelf ? ` (SHELF: ${metadata.shelf})` : ""}
    </Grid.Column>
  );
};

ItemCirculationShelf.propTypes = {
  metadata: PropTypes.object.isRequired,
};
