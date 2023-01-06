import React from "react";
import { toShortDateTime } from "@inveniosoftware/react-invenio-app-ils";
import PropTypes from "prop-types";
import { Label, Icon } from "semantic-ui-react";
import { DateTime } from "luxon";

export class ImporterDateLabel extends React.Component {
  dateLabel = (startTime) => {
    const date = toShortDateTime(DateTime.fromISO(startTime));
    return (
      <>
        {" "}
        <Icon name="calendar" /> <Label basic>{date}</Label>{" "}
      </>
    );
  };

  render() {
    const { data } = this.props;

    if (!data) return this.dateLabel("Missing date");

    return this.dateLabel(data.start_time);
  }
}

ImporterDateLabel.propTypes = {
  data: PropTypes.object.isRequired,
};
