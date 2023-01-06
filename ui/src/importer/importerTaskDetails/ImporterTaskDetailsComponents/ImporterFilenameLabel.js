import React from "react";
import PropTypes from "prop-types";
import { Label, Icon } from "semantic-ui-react";

export class ImporterFilenameLabel extends React.Component {
  filenameLabel = (filename) => {
    return (
      <>
        {" "}
        <Icon name="file" /> <Label basic>{filename}</Label>{" "}
      </>
    );
  };

  render() {
    const { data } = this.props;

    if (!data) return this.filenameLabel("Missing filename");

    return this.filenameLabel(data.original_filename);
  }
}

ImporterFilenameLabel.propTypes = {
  data: PropTypes.object.isRequired,
};
