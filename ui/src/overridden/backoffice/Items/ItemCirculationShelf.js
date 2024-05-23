import { isEmpty } from "lodash";
import React from "react";
import { Grid, Icon } from "semantic-ui-react";
import PropTypes from "prop-types";

export const ItemCirculationShelf = ({ metadata }) => {
  let callNumber = {};
  if (!isEmpty(metadata.identifiers)) {
    callNumber = metadata.identifiers.find(
      (identifier) => identifier.scheme === "CALL_NUMBER"
    );
  }
  return (
    <Grid.Column width={6}>
      <Icon name="map pin" />
      Call number: {callNumber ? callNumber.value : "missing"} (SHELF:{" "}
      {metadata.shelf ? metadata.shelf : "missing"})
    </Grid.Column>
  );
};

ItemCirculationShelf.propTypes = {
  metadata: PropTypes.object.isRequired,
};
