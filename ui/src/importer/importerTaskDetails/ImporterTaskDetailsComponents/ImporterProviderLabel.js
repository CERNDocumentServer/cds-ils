import React from "react";
import PropTypes from "prop-types";
import { Label, Icon } from "semantic-ui-react";

export class ImporterProviderLabel extends React.Component {
  providerLabel = (provider) => {
    return (
      <>
        {" "}
        <Icon name="building" /> <Label basic>{provider}</Label>{" "}
      </>
    );
  };

  render() {
    const { data } = this.props;

    if (!data) return this.providerLabel("Missing provider");

    return this.providerLabel(data.provider);
  }
}

ImporterProviderLabel.propTypes = {
  data: PropTypes.object.isRequired,
};
