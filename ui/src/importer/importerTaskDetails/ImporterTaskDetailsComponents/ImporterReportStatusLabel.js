import React from "react";
import PropTypes from "prop-types";
import { Icon, Label } from "semantic-ui-react";

export class ImporterReportStatusLabel extends React.Component {
  constructor(props) {
    super(props);

    this.labels = {
      SUCCEEDED: <Label color="green">Import successful</Label>,
      CANCELLED: <Label color="yellow">Import cancelled</Label>,
      IMPORTING: (
        <Label color="blue">
          <Icon loading name="circle notch" /> Importing literature
        </Label>
      ),
      LOADING: <Label color="grey">Fetching status</Label>,
      FAILED: <Label color="yellow">Import failed</Label>,
    };
  }

  relevantLabel = (status) => {
    return (
      <>
        {" "}
        <Icon name="upload" /> {this.labels[status]}{" "}
      </>
    );
  };

  render() {
    const { data, isLoading } = this.props;

    if (!data) return this.relevantLabel("LOADING");

    if (isLoading) return this.relevantLabel("IMPORTING");

    return this.relevantLabel(data.status);
  }
}

ImporterReportStatusLabel.propTypes = {
  data: PropTypes.object.isRequired,
  isLoading: PropTypes.bool.isRequired,
};
