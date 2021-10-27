import React from 'react';
import PropTypes from 'prop-types';
import {
  Button,
  Message,
  Segment,
  Label,
  Grid,
  Icon,
  Divider,
} from 'semantic-ui-react';
import _isEmpty from 'lodash/isEmpty';
import _isNull from 'lodash/isNull';
import _get from 'lodash/get';
import _cloneDeep from 'lodash/cloneDeep';
import { CancelImportTask } from './cancelImportTask';
import { RenderStatistics } from './ImportStats';
import { ImportedTable } from './ImportedTable';
import { ImportedSearch } from './ImportedSearch';
import { CdsBackOfficeRoutes } from '../../overridden/routes/BackofficeUrls';
import { Link } from 'react-router-dom';
import { importerApi } from '../../api/importer';
import {
  invenioConfig,
  NotFound,
} from '@inveniosoftware/react-invenio-app-ils';

export class ImportedDocuments extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      importCompleted: false,
      data: null,
      isLoading: false,
      error: null,
      selectedResult: 'records',
      searchText: '',
      activePage: 1,
      statistics: {
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
          filterFunction: record => !_isNull(record.eitem),
        },
        records_with_serials: {
          text: 'Records with Serials',
          value: 0,
          filterFunction: record => !_isEmpty(record.series),
        },
      },
      filteredRecords: null,
    };
    this.mode = '';
    this.status = '';
    this.lastIndex = 0;
  }

  componentDidMount() {
    const { taskId } = this.props;
    this.intervalId = setInterval(
      () => this.checkForData(taskId),
      invenioConfig.IMPORTER.fetchTaskStatusIntervalSecs
    );
    this.checkForData(taskId);
  }

  componentWillUnmount = () => {
    this.intervalId && clearInterval(this.intervalId);
  };

  checkForData = async () => {
    const { importCompleted, data, intervalId } = this.state;
    const { taskId } = this.props;

    if (importCompleted) {
      this.intervalId && clearInterval(intervalId);

      return;
    }

    try {
      const nextEntry = _get(data, 'loaded_entries', 0);
      const response = await importerApi.check(taskId, nextEntry);
      if (response.data.status !== 'RUNNING') {
        this.setState({
          importCompleted: true,
          isLoading: false,
          data: response.data,
        });
      } else {
        this.setState({
          isLoading: true,
          data: response.data,
        });
      }
      this.filteredRecords();
      this.calculateMode();
      this.calculateStatus();
      this.calculateStatistics(response.data);
    } catch (error) {
      this.setState({ error, isLoading: false });
    }
  };

  calculateMode = () => {
    const { data } = this.state;
    switch (data.mode) {
      case 'IMPORT':
        this.mode = (
          <Label color="blue" basic>
            Import
          </Label>
        );
        break;
      case 'DELETE':
        this.mode = (
          <Label color="red" basic>
            Delete
          </Label>
        );
        break;
      case 'PREVIEW_IMPORT':
        this.mode = (
          <Label color="teal" basic>
            Preview (import)
          </Label>
        );
        break;
      case 'PREVIEW_DELETE':
        this.mode = (
          <Label color="teal" basic>
            Preview (delete)
          </Label>
        );
        break;
      case 'ERROR':
        this.mode = (
          <Label color="red" basic>
            Error
          </Label>
        );
        break;
      default:
        throw Error('There was a problem processing the mode.');
    }
  };

  statusLabel = () => {
    const { data, isLoading } = this.state;
    if (!data) return <Label color="grey">Fetching status</Label>;
    if (isLoading)
      return (
        <Label color="blue">
          <Icon loading name="circle notch" /> Importing literature
        </Label>
      );
    switch (data.status) {
      case 'SUCCEEDED':
        return <Label color="green">Import successfull</Label>;
      case 'CANCELLED':
        return <Label color="yellow">Import cancelled</Label>;
      default:
        return <Label color="red">Import failed</Label>;
    }
  };

  calculateStatus = () => {
    this.status = this.statusLabel();
  };

  calculateStatistics = data => {
    const { statistics } = this.state;
    let stats = _cloneDeep(statistics);
    const records = data.records;
    const newRecords = records.slice(this.lastIndex, records.length);

    this.lastIndex += newRecords.length;
    stats.records.value = `${data.loaded_entries}/${data.entries_count}`;

    data.mode.includes('DELETE')
      ? delete stats.records_created
      : delete stats.records_deleted;

    for (const statistic in stats) {
      const filterFunc = stats[statistic].filterFunction;
      if (statistic !== 'records') {
        stats[statistic].value += newRecords.filter(record =>
          filterFunc(record)
        ).length;
      }
    }
    this.setState({
      statistics: stats,
    });
  };

  renderErrorMessage = () => {
    return (
      <Message negative>
        <Message.Header>Failed to import</Message.Header>
        <p>
          The import of the literature failed, please try again. <br />
          If this error persists contact our technical support.
        </p>
      </Message>
    );
  };

  renderImportReportHeader = () => {
    const { data, error } = this.state;
    const noErrors = !error;

    return noErrors ? (
      <Grid>
        <Grid.Column floated="left" width={12}>
          <Button
            className="default-margin-top"
            labelPosition="left"
            icon="left arrow"
            content="Import other files"
            loading={!data?.status}
            disabled={!data?.status}
            as={Link}
            to={CdsBackOfficeRoutes.importerCreate}
          />
          {this.renderCancelButton()}
        </Grid.Column>
        <Grid.Column textAlign="right" floated="right" width={4}>
          <ImportedSearch onSearchChange={this.onSearchChange} />
        </Grid.Column>
      </Grid>
    ) : null;
  };

  applyFilter = key => {
    this.setState(
      {
        selectedResult: key,
      },
      () => this.filteredRecords()
    );
  };

  onSearchChange = text => {
    this.setState(
      {
        searchText: text,
      },
      () => this.filteredRecords()
    );
  };

  setActivePage = page => {
    this.setState({
      activePage: page,
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

  filteredRecords = () => {
    const { statistics, data, selectedResult } = this.state;
    const selectedFilterFunc = statistics[selectedResult].filterFunction;
    const records = data.records;

    const filteredRecords = records
      .filter(record => selectedFilterFunc(record))
      .filter(record => this.filterBySearchText(record));
    this.setState({
      filteredRecords: filteredRecords,
      activePage: 1,
    });
  };

  renderCancelButton = () => {
    const { isLoading } = this.state;
    const { taskId } = this.props;

    return (
      isLoading && (
        <>
          <CancelImportTask logId={taskId} />{' '}
          <Icon loading name="circle notch" />
          This may take a while. You may leave the page, the process will
          continue in background.
        </>
      )
    );
  };

  renderContent = () => {
    const {
      data,
      statistics,
      selectedResult,
      filteredRecords,
      activePage,
      error,
    } = this.state;

    const dataAvailable = !_isEmpty(data);
    const filteredRecordsAvailable = !_isEmpty(filteredRecords);
    const filteredRecordsNotNull = !_isNull(filteredRecords);
    const errorWhileFetching = !_isEmpty(data) && data?.status === 'FAILED';
    const entriesReady =
      (data?.loaded_entries || data?.loaded_entries === 0) &&
      data?.entries_count;

    if (error) {
      return <NotFound title="Task not found" />;
    }

    if (errorWhileFetching) {
      return this.renderErrorMessage(data);
    }

    const HeaderComponent = () =>
      entriesReady && dataAvailable ? (
        <Grid className="middle aligned">
          <Grid.Column width={3}>
            <Segment>
              Mode: {this.mode}
              <Divider />
              Status: {this.status}
            </Segment>
          </Grid.Column>
          <Grid.Column width={13}>
            <RenderStatistics
              statistics={statistics}
              selectedResult={selectedResult}
              applyFilter={this.applyFilter}
            />
          </Grid.Column>
        </Grid>
      ) : (
        <span>Processing file...</span>
      );

    const BodyComponent = () => {
      if (filteredRecordsAvailable) {
        return (
          <ImportedTable
            records={filteredRecords}
            activePage={activePage}
            onPageChange={this.setActivePage}
          />
        );
      } else if (filteredRecordsNotNull) {
        return (
          <Message>
            <Message.Header>No records found.</Message.Header>
            <p>No records found with the selected filter.</p>
          </Message>
        );
      }
    };

    return (
      <>
        {HeaderComponent()}
        {BodyComponent()}
      </>
    );
  };

  render() {
    return (
      <>
        {this.renderImportReportHeader()}
        {this.renderContent()}
      </>
    );
  }
}

ImportedDocuments.propTypes = {
  taskId: PropTypes.string.isRequired,
};
