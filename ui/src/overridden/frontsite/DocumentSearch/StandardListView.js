import React from "react";
import { Label } from "semantic-ui-react";
import PropTypes from "prop-types";

export const StandardListView = ({ metadata, ...props }) => {
  const renderLabels = (numbers) => {
    return numbers.map((number) => (
      <Label
        className="standard-number-list-view"
        color="grey"
        image
        size="small"
        key={number}
      >
        Standard number
        <Label.Detail>{number}</Label.Detail>
      </Label>
    ));
  };

  const standardNumbers = metadata.identifiers
    ? metadata.identifiers
        .filter((sn) => sn.scheme === "STANDARD_NUMBER")
        .map((a) => a.value)
    : null;

  return standardNumbers ? <div>{renderLabels(standardNumbers)}</div> : null;
};

StandardListView.propTypes = {
  metadata: PropTypes.object.isRequired,
};
