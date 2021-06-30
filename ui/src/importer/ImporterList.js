import {
  ResultsTable,
  withCancel,
} from '@inveniosoftware/react-invenio-app-ils';
import _isEmpty from 'lodash/isEmpty';
import { DateTime } from 'luxon';
import React, { Component } from 'react';
import { Link } from 'react-router-dom';
import { Button, Grid, Icon, Label, Loader } from 'semantic-ui-react';
import { importerApi } from '../api/importer';
import { BackOfficeRouteGenerators } from '../overridden/routes/BackofficeUrls';

export const modeFormatter = mode => {
  switch (mode) {
    case 'IMPORT':
      return (
        <Label color="blue" basic>
          <Icon name="plus" />
          Import
        </Label>
      );
    case 'DELETE':
      return (
        <Label color="red" basic>
          <Icon name="minus" />
          Delete
        </Label>
      );
    case 'PREVIEW_IMPORT':
      return (
        <Label color="teal" basic>
          <Icon name="plus" />
          Preview (import)
        </Label>
      );
    case 'PREVIEW_DELETE':
      return (
        <Label color="teal" basic>
          <Icon name="plus" />
          Preview (delete)
        </Label>
      );
    default:
      return null;
  }
};

export class ImporterList extends Component {
  state = {
    isLoading: true,
    error: null,
    data: null,
  };

  componentDidMount() {
    this.fetchData();
  }

  componentWillUnmount() {
    this.cancellableFetchStats && this.cancellableFetchStats.cancel();
  }

  emptyMessage = 'No past import tasks.';

  idFormatter = ({ col, row }) => {
    const id = row[col.field];
    return (
      <Link to={BackOfficeRouteGenerators.importerDetailsFor(id)}>{id}</Link>
    );
  };

  stateFormatter = ({ col, row }) => {
    switch (row[col.field]) {
      case 'RUNNING':
        return (
          <Icon name="circle notch" loading aria-label="Import in progress" />
        );
      case 'SUCCEEDED':
        return (
          <Icon name="check circle" color="green" aria-label="Completed" />
        );
      case 'FAILED':
        return <Icon name="times circle" color="red" aria-label="Failed" />;
      default:
        return null;
    }
  };

  datetimeFormatter = ({ col, row }) => {
    const datetime = DateTime.fromISO(row[col.field]);
    return datetime.toLocaleString(
      Object.assign(DateTime.DATETIME_SHORT, { locale: 'en-GB' })
    );
  };

  durationFormatter = ({ col, row }) => {
    const endTime = row[col.field];
    if (endTime) {
      const t0 = DateTime.fromISO(row['start_time']);
      const t1 = DateTime.fromISO(row[col.field]);
      const duration = t0
        .until(t1)
        .toDuration()
        .shiftTo('hours', 'minutes', 'seconds');
      const parts = [];
      if (duration.hours > 0) {
        parts.push(duration.hours, `hour${duration.hours !== 1 ? 's' : ''}`);
      }
      if (duration.hours > 0 || duration.minutes > 0) {
        parts.push(
          duration.minutes,
          `minute${duration.minutes !== 1 ? 's' : ''}`
        );
      }
      const seconds = Math.round(duration.seconds);
      parts.push(seconds, `second${seconds !== 1 ? 's' : ''}`);
      return parts.join(' ');
    } else {
      return 'Ongoing';
    }
  };

  labelFormatter = ({ col, row }) => <Label>{row[col.field]}</Label>;

  optionalFormatter = ({ col, row }) => {
    const value = row[col.field];
    return value != null ? value : '';
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

  columns = [
    { title: 'ID', field: 'id', formatter: this.idFormatter },
    { title: 'Status', field: 'state', formatter: this.stateFormatter },
    { title: 'Date', field: 'start_time', formatter: this.datetimeFormatter },
    { title: 'Duration', field: 'end_time', formatter: this.durationFormatter },
    {
      title: 'Literature in file',
      field: 'entries_count',
      formatter: this.optionalFormatter,
    },
    { title: 'Provider', field: 'provider', formatter: this.labelFormatter },
    {
      title: 'Mode',
      field: 'mode',
      formatter: ({ col, row }) => modeFormatter(row[col.field]),
    },
    {
      title: 'Source type',
      field: 'source_type',
      formatter: this.labelFormatter,
    },
    {
      title: '',
      field: 'id',
      formatter: this.viewFormatter,
    },
  ];

  fetchData = async () => {
    this.setState({ isLoading: true, error: null });

    this.cancellableFetchStats = withCancel(importerApi.list());
    try {
      const response = await this.cancellableFetchStats.promise;
      this.setState({ data: response.data, isLoading: false });
    } catch (error) {
      if (error !== 'UNMOUNTED') {
        this.setState({ error: error, isLoading: false });
      }
    }
  };

  render() {
    const { isLoading, error, data } = this.state;

    return isLoading && _isEmpty(error) ? (
      <Loader active inline="centered" />
    ) : (
      <>
        <ResultsTable
          data={data}
          columns={this.columns}
          renderEmptyResultsElement={() => this.emptyMessage}
        />
        {!_isEmpty(data) && (
          <Grid>
            <Grid.Column width={16} textAlign="center">
              Showing the last {data.length} rows.
            </Grid.Column>
          </Grid>
        )}
      </>
    );
  }
}
