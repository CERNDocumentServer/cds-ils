import React from 'react';
import PropTypes from 'prop-types';
import { Message, Segment, Grid, Divider } from 'semantic-ui-react';
import _isEmpty from 'lodash/isEmpty';
import _isNull from 'lodash/isNull';
import { RenderStatistics } from './ImporterTaskDetailsComponents/ImportStats';
import { ImportedTable } from './ImporterTaskDetailsComponents/ImportedTable';
import { ImporterReportHeader } from './ImporterTaskDetailsComponents/ImporterReportHeader';
import { HttpError } from '@inveniosoftware/react-invenio-app-ils';
import { ImporterReportStatusLabel } from './ImporterTaskDetailsComponents/ImporterReportStatusLabel';
import { ImporterReportMode } from './ImporterTaskDetailsComponents/ImporterReportMode';

export class ImportedDocuments extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      selectedResult: 'records',
      searchText: '',
      activePage: 1,
    };

    this.lastIndex = 0;
    this.statistics = {
      records: {
        text: 'Records',
        value: '',
        filterFunction: record => record,
      },
      records_created: {
        text: 'Records created',
        value: 0,
        filterFunction: record => record.action === 'create',
      },
      records_deleted: {
        text: 'Records deleted',
        value: 0,
        filterFunction: record => record.action === 'delete',
      },
      records_updated: {
        text: 'Records updated',
        value: 0,
        filterFunction: record => record.action === 'update',
      },
      records_with_errors: {
        text: 'Records with errors',
        value: 0,
        filterFunction: record => _isNull(record.action),
      },
      records_with_item: {
        text: 'Records with eItem',
        value: 0,
        filterFunction: record => !_isEmpty(record.eitem),
      },
      records_with_serials: {
        text: 'Records with Serials',
        value: 0,
        filterFunction: record => !_isEmpty(record.series),
      },
    };
  }

  calculateStatistics = (data, stats) => {
    const records = data.records;
    const newRecords = records.slice(this.lastIndex, records.length);

    stats.records.value = `${data.loaded_entries}/${data.entries_count}`;

    data.mode.includes('DELETE')
      ? delete stats.records_created
      : delete stats.records_deleted;

    for (const statistic in stats) {
      const filterFunc = stats[statistic].filterFunction;

      const isFullRecords = statistic === 'records';
      // the full records have no filter function
      if (isFullRecords) continue;

      stats[statistic].value += newRecords.filter(record =>
        filterFunc(record)
      ).length;
    }

    this.lastIndex += newRecords.length;

    return stats;
  };

  applyFilter = key => {
    this.setState({
      selectedResult: key,
      activePage: 1,
    });
  };

  onSearchChange = text => {
    this.setState({
      searchText: text,
      activePage: 1,
    });
  };

  filterBySearchText = record => {
    const { searchText } = this.state;

    if (searchText === '') {
      return true;
    }

    const lowerSearchText = searchText.toLowerCase();
    return (
      record.entry_recid?.toLowerCase().includes(lowerSearchText) ||
      record.output_pid?.toLowerCase().includes(lowerSearchText) ||
      record.document?.title.toLowerCase().includes(lowerSearchText) ||
      record.eitem?.output_pid?.toLowerCase().includes(lowerSearchText) ||
      record.series?.filter(serie =>
        serie.output_pid?.toLowerCase().includes(lowerSearchText)
      ).length > 0
    );
  };

  filteredRecords = data => {
    const { selectedResult } = this.state;
    const selectedFilterFunc = this.statistics[selectedResult].filterFunction;

    if (!data) return null;

    const records = data.records;

    const filteredRecords = records
      .filter(record => selectedFilterFunc(record))
      .filter(record => this.filterBySearchText(record));

    return filteredRecords;
  };

  render() {
    const { data, taskId, isLoading, error } = this.props;
    const { selectedResult, activePage } = this.state;
    const dataAvailable = !_isEmpty(data);

    const errorWhileFetching = !_isEmpty(data) && data?.status === 'FAILED';
    const entriesReady =
      (data?.loaded_entries || data?.loaded_entries === 0) &&
      data?.entries_count;

    if (error) {
      const {
        response: {
          data: { message, status },
        },
      } = error;
      return <HttpError title={status} message={message} isBackOffice />;
    }

    if (errorWhileFetching) {
      return (
        <Message negative>
          <Message.Header>Failed to import</Message.Header>
          <p>
            The import of the literature failed, please try again. <br />
            If this error persists contact our technical support.
          </p>
        </Message>
      );
    }

    const filteredRecords = this.filteredRecords(data);

    const filteredRecordsAvailable = !_isEmpty(filteredRecords);
    const filteredRecordsNotNull = !_isNull(filteredRecords);

    return (
      <>
        <ImporterReportHeader
          taskId={taskId}
          isImporting={isLoading}
          onSearch={this.onSearchChange}
          isLoadingFile={!data?.status}
        />

        {entriesReady && dataAvailable ? (
          <Grid className="middle aligned">
            <Grid.Column width={3}>
              <Segment>
                <ImporterReportMode data={data} />
                <Divider />
                <ImporterReportStatusLabel data={data} isLoading={isLoading} />
              </Segment>
            </Grid.Column>
            <Grid.Column width={13}>
              <RenderStatistics
                statistics={this.calculateStatistics(data, this.statistics)}
                selectedResult={selectedResult}
                applyFilter={this.applyFilter}
              />
            </Grid.Column>
          </Grid>
        ) : (
          <span>Processing file...</span>
        )}

        {filteredRecordsAvailable ? (
          <ImportedTable
            records={filteredRecords}
            activePage={activePage}
            onPageChange={this.setActivePage}
          />
        ) : (
          filteredRecordsNotNull && (
            <Message>
              <Message.Header>No records found.</Message.Header>
              <p>No records found with the selected filter.</p>
            </Message>
          )
        )}
      </>
    );
  }
}

ImportedDocuments.propTypes = {
  taskId: PropTypes.string.isRequired,
  data: PropTypes.object.isRequired,
  isLoading: PropTypes.bool.isRequired,
  error: PropTypes.object.isRequired,
};
