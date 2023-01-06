import React from "react";
import PropTypes from "prop-types";
import { Label, Icon } from "semantic-ui-react";

export class ImporterReportMode extends React.Component {
  constructor(props) {
    super(props);

    this.labels = {
      IMPORT: (
        <Label color="blue" basic>
          Import
        </Label>
      ),
      DELETE: (
        <Label color="red" basic>
          Delete
        </Label>
      ),
      PREVIEW_IMPORT: (
        <Label color="teal" basic>
          Preview (import)
        </Label>
      ),
      PREVIEW_DELETE: (
        <Label color="teal" basic>
          Preview (delete)
        </Label>
      ),
      ERROR: (
        <Label color="red" basic>
          Error
        </Label>
      ),
    };
  }

  render() {
    const { data } = this.props;

    return (
      <>
        {" "}
        <Icon name="cog" /> {this.labels[data.mode]}{" "}
      </>
    );
  }
}

ImporterReportMode.propTypes = {
  data: PropTypes.object.isRequired,
};
