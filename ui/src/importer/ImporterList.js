import {
  ResultsTable,
  withCancel,
  Pagination,
  toShortDateTime,
} from "@inveniosoftware/react-invenio-app-ils";
import _isEmpty from "lodash/isEmpty";
import { DateTime } from "luxon";
import React, { Component } from "react";
import { Link } from "react-router-dom";
import { Button, Icon, Label, Loader, Popup } from "semantic-ui-react";
import { importerApi } from "../api/importer";
import { BackOfficeRouteGenerators } from "../overridden/routes/BackofficeUrls";

export const modeFormatter = (mode) => {
  switch (mode) {
    case "IMPORT":
      return (
        <Label color="blue" basic>
          Import
        </Label>
      );
    case "DELETE":
      return (
        <Label color="red" basic>
          Delete
        </Label>
      );
    case "PREVIEW_IMPORT":
      return (
        <Label color="teal" basic>
          Preview (import)
        </Label>
      );
    case "PREVIEW_DELETE":
      return (
        <Label color="teal" basic>
          Preview (delete)
        </Label>
      );
    default:
      return null;
  }
};

export class ImporterList extends Component {
  constructor(props) {
    super(props);
    this.state = {
      isLoading: true,
      error: null,
      data: null,
      activePage: 1,
    };
    this.pageSize = 15;
    this.columns = [
      { title: "ID", field: "id", formatter: this.idFormatter },
      { title: "Status", field: "status", formatter: this.stateFormatter },
      { title: "Date", field: "start_time", formatter: this.datetimeFormatter },
      {
        title: "Duration",
        field: "end_time",
        formatter: this.durationFormatter,
      },
      {
        title: "Records in file",
        field: "entries_count",
        formatter: this.optionalFormatter,
      },
      { title: "Provider", field: "provider", formatter: this.labelFormatter },
      {
        title: "Mode",
        field: "mode",
        formatter: ({ col, row }) => modeFormatter(row[col.field]),
      },
      {
        title: "Original Filename",
        field: "original_filename",
        formatter: this.trimFormatter,
      },
      {
        title: "Source type",
        field: "source_type",
        formatter: this.labelFormatter,
      },
      {
        title: "Strict JSON rules",
        field: "ignore_missing_rules",
        formatter: this.ignoreMissingFormatter,
      },
      {
        title: "",
        field: "id",
        formatter: this.viewFormatter,
      },
    ];
  }

  componentDidMount() {
    this.fetchData();
  }

  componentWillUnmount() {
    this.cancellableFetchStats && this.cancellableFetchStats.cancel();
  }

  emptyMessage = "No past import tasks.";

  idFormatter = ({ col, row }) => {
    const id = row[col.field];
    return <Link to={BackOfficeRouteGenerators.importerDetailsFor(id)}>{id}</Link>;
  };

  stateFormatter = ({ col, row }) => {
    switch (row[col.field]) {
      case "RUNNING":
        return <Icon name="circle notch" loading aria-label="Import in progress" />;
      case "SUCCEEDED":
        return <Icon name="check circle" color="green" aria-label="Completed" />;
      case "CANCELLED":
        return <Icon name="times circle" color="yellow" aria-label="Failed" />;
      case "FAILED":
        return <Icon name="exclamation circle" color="red" aria-label="Failed" />;
      default:
        return null;
    }
  };

  datetimeFormatter = ({ col, row }) => {
    return toShortDateTime(DateTime.fromISO(row[col.field]));
  };

  durationFormatter = ({ col, row }) => {
    const endTime = row[col.field];
    if (endTime) {
      const t0 = DateTime.fromISO(row["start_time"]);
      const t1 = DateTime.fromISO(row[col.field]);
      const duration = t0.until(t1).toDuration().shiftTo("hours", "minutes", "seconds");
      const parts = [];
      if (duration.hours > 0) {
        parts.push(duration.hours, `hour${duration.hours !== 1 ? "s" : ""}`);
      }
      if (duration.hours > 0 || duration.minutes > 0) {
        parts.push(duration.minutes, `minute${duration.minutes !== 1 ? "s" : ""}`);
      }
      const seconds = Math.round(duration.seconds);
      parts.push(seconds, `second${seconds !== 1 ? "s" : ""}`);
      return parts.join(" ");
    } else {
      return "Ongoing";
    }
  };

  labelFormatter = ({ col, row }) => <Label>{row[col.field]}</Label>;

  ignoreMissingFormatter = ({ col, row }) => {
    const ignoreMissingRules = row[col.field];
    return !ignoreMissingRules ? (
      <Icon name="checkmark box" color="green" />
    ) : (
      <Icon name="close" color="red" />
    );
  };

  optionalFormatter = ({ col, row }) => {
    const value = row[col.field];
    return value != null ? value : "";
  };

  trimFormatter = ({ col, row }) => {
    const value = row[col.field];
    return value != null ? (
      <Popup
        content={value}
        mouseEnterDelay={100}
        trigger={<p>{value.length > 18 ? value.substring(0, 15) + "..." : value}</p>}
      />
    ) : (
      ""
    );
  };

  viewFormatter = ({ col, row }) => {
    const id = row[col.field];
    return (
      <Button
        as={Link}
        to={BackOfficeRouteGenerators.importerDetailsFor(id)}
        icon="eye"
      />
    );
  };

  fetchData = async () => {
    this.setState({ isLoading: true, error: null });

    this.cancellableFetchStats = withCancel(importerApi.list());
    try {
      const response = await this.cancellableFetchStats.promise;
      this.setState({ data: response.data, isLoading: false });
    } catch (error) {
      if (error !== "UNMOUNTED") {
        this.setState({ error: error, isLoading: false });
      }
    }
  };

  onPageChange = (page) => {
    this.setState({ activePage: page });
  };

  render() {
    const { isLoading, error, data, activePage } = this.state;
    return isLoading && _isEmpty(error) && _isEmpty(data) ? (
      <Loader active inline="centered" />
    ) : (
      <ResultsTable
        data={data}
        columns={this.columns}
        totalHitsCount={data.length}
        showMaxRows={this.pageSize}
        currentPage={activePage}
        renderEmptyResultsElement={() => this.emptyMessage}
        showFooterSummary={false}
        paginationComponent={
          <Pagination
            currentPage={activePage}
            currentSize={this.pageSize}
            totalResults={data.length}
            onPageChange={this.onPageChange}
          />
        }
      />
    );
  }
}
