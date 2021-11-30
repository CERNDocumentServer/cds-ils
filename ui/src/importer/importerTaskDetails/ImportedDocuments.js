import React from 'react';
import PropTypes from 'prop-types';
import { Grid, Message, Segment } from 'semantic-ui-react';
import _isEmpty from 'lodash/isEmpty';
import _isNull from 'lodash/isNull';
import { RenderStatistics } from './ImporterTaskDetailsComponents/ImportStats';
import { ImportedTable } from './ImporterTaskDetailsComponents/ImportedTable';
import { ImporterReportHeader } from './ImporterTaskDetailsComponents/ImporterReportHeader';
import { HttpError } from '@inveniosoftware/react-invenio-app-ils';
import { ImporterReportStatusLabel } from './ImporterTaskDetailsComponents/ImporterReportStatusLabel';
import { ImporterReportMode } from './ImporterTaskDetailsComponents/ImporterReportMode';
import { ImporterProviderLabel } from './ImporterTaskDetailsComponents/ImporterProviderLabel';
import { ImporterFilenameLabel } from './ImporterTaskDetailsComponents/ImporterFilenameLabel';
import { ImporterDateLabel } from './ImporterTaskDetailsComponents/ImporterDateLabel';

export class ImportedDocuments extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      searchText: '',
    };

    this.lastIndex = 0;
  }

  onSearchChange = text => {
    const { setPage } = this.props;

    setPage(1);

    this.setState({
      searchText: text,
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
    if (!data) return null;

    const records = data.records;

    return records.filter(record => this.filterBySearchText(record));
  };

  render() {
    const {
      data,
      taskId,
      isLoading,
      isImporting,
      error,
      filterType,
      page,
      pageSize,
      setPage,
      setFilterType,
    } = this.props;
    const dataAvailable = !_isEmpty(data);

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

    const filteredRecords = this.filteredRecords(data);

    const filteredRecordsAvailable = !_isEmpty(filteredRecords);
    const filteredRecordsNotNull = !_isNull(filteredRecords);

    return (
      <>
        <ImporterReportHeader
          taskId={taskId}
          isImporting={isImporting}
          onSearch={this.onSearchChange}
          isLoadingFile={!data?.status || isLoading}
        />

        {entriesReady && dataAvailable ? (
          <>
            <Segment>
              <Grid columns={5} divided>
                <Grid.Column width={2}>
                  <ImporterReportMode data={data} />
                </Grid.Column>
                <Grid.Column width={3}>
                  <ImporterReportStatusLabel
                    data={data}
                    isLoading={isImporting}
                  />
                </Grid.Column>
                <Grid.Column width={2}>
                  <ImporterProviderLabel data={data} />
                </Grid.Column>
                <Grid.Column width={2}>
                  <ImporterDateLabel data={data} />
                </Grid.Column>
                <Grid.Column width={7}>
                  <ImporterFilenameLabel data={data} />
                </Grid.Column>
              </Grid>
            </Segment>
            <Segment>
              <RenderStatistics
                statistics={data.statistics}
                selectedResult={filterType}
                applyFilter={setFilterType}
              />
            </Segment>
          </>
        ) : (
          <span>Processing file...</span>
        )}

        {filteredRecordsAvailable ? (
          <ImportedTable
            records={filteredRecords}
            activePage={page}
            onPageChange={setPage}
            pageSize={pageSize}
            totalPages={data.total_pages}
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
  isImporting: PropTypes.bool.isRequired,
  error: PropTypes.object.isRequired,
  page: PropTypes.number.isRequired,
  pageSize: PropTypes.number.isRequired,
  filterType: PropTypes.string.isRequired,
  setPage: PropTypes.func.isRequired,
  setFilterType: PropTypes.func.isRequired,
};
