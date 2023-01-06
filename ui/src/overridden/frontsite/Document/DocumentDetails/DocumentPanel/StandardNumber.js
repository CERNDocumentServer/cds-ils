import React from "react";
import { Label } from "semantic-ui-react";
import PropTypes from "prop-types";
import _isEmpty from "lodash/isEmpty";

export const StandardNumber = ({ metadata, ...props }) => {
  const renderLabels = (numbers) => {
    return numbers.map((number) => (
      <Label
        className="default-margin-bottom standard-number"
        color="grey"
        image
        key={number}
      >
        Standard number
        <Label.Detail>{number}</Label.Detail>
      </Label>
    ));
  };

  let standardNumbers = [];
  if (metadata.identifiers) {
    standardNumbers = metadata.identifiers.filter(
      (sn) => sn.scheme === "STANDARD_NUMBER"
    );
    standardNumbers = standardNumbers.map((a) => a.value);
  }

  return _isEmpty(standardNumbers) ? null : <div>{renderLabels(standardNumbers)}</div>;
};

StandardNumber.propTypes = {
  metadata: PropTypes.object.isRequired,
};
