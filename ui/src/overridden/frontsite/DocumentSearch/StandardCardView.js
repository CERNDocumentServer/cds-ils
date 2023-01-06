import React from "react";
import { Label } from "semantic-ui-react";
import PropTypes from "prop-types";

export const StandardCardView = ({ metadata, ...props }) => {
  const first = metadata.identifiers
    ? metadata.identifiers
        .filter((sn) => sn.scheme === "STANDARD_NUMBER")
        .map((a) => a.value)
        .shift()
    : null;

  return first ? (
    <Label
      basic
      size="small"
      color="grey"
      className="margin-bottom-with-standard-number"
    >
      {first}
    </Label>
  ) : null;
};

StandardCardView.propTypes = {
  metadata: PropTypes.object.isRequired,
};
