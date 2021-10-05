import React from 'react';
import PropTypes from 'prop-types';
import {
  Button,
  Message,
  Segment,
  Statistic,
  Label,
  Grid,
  Icon,
  Divider,
} from 'semantic-ui-react';
import _isEmpty from 'lodash/isEmpty';
import _isNull from 'lodash/isNull';
import _get from 'lodash/get';
import { CancelImportTask } from './cancelImportTask';
import { ImportedTable } from './ImportedTable';
import { CdsBackOfficeRoutes } from '../../overridden/routes/BackofficeUrls';
import { Link } from 'react-router-dom';
import { importerApi } from '../../api/importer';
import { invenioConfig } from '@inveniosoftware/react-invenio-app-ils';

export class ImportedDocuments extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      importCompleted: false,
      data: null,
      isLoading: true,
      selectedResult: 'records',
      statistics: {
        records: {
          text: 'Records',
          value: '',
          filterFunction: a => a,
          filteredRecords: [],
        },
        records_created: {
          text: 'Records created',
          value: '',
          filterFunction: a => a.action === 'create',
          filteredRecords: [],
        },
        records_updated: {
          text: 'Records updated',
          value: '',
          filterFunction: a => a.action === 'update',
          filteredRecords: [],
        },
        records_with_errors: {
          text: 'Records with errors',
          value: '',
          filterFunction: a => _isNull(a.action),
          filteredRecords: [],
        },
        records_with_item: {
          text: 'Records with eItem',
          value: '',
          filterFunction: a => !_isNull(a.eitem),
          filteredRecords: [],
        },
        records_with_serials: {
          text: 'Records with Serials',
          value: '',
          filterFunction: a => !_isEmpty(a.series),
          filteredRecords: [],
        },
      },
      mode: '',
      status: '',
      currentFilteredRecords: [],
    };
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
    const { importCompleted, data } = this.state;
    const { taskId } = this.props;
    if (!importCompleted) {
      const nextEntry = _get(data, 'loaded_entries', 0);
      const response = await importerApi.check(taskId, nextEntry);
      const responseData = response.data;

      if (responseData) {
        responseData.records = _get(responseData, 'records', []);
      }
      if (response.data.status !== 'RUNNING') {
        this.setState({
          importCompleted: true,
          isLoading: false,
          data: responseData,
        });
      } else {
        this.setState({
          isLoading: true,
          data: responseData,
        });
      }
      this.modeLabel();
      this.statusLabel();
      this.calculateStatistics();
    } else {
      this.intervalId && clearInterval(this.intervalId);
    }
  };

  modeLabel = () => {
    let { data, mode } = this.state;
    switch (data.mode) {
      case 'IMPORT':
        mode = (
          <Label color="blue" basic>
            Import
          </Label>
        );
        break;
      case 'DELETE':
        mode = (
          <Label color="red" basic>
            Delete
          </Label>
        );
        break;
      case 'PREVIEW_IMPORT':
        mode = (
          <Label color="teal" basic>
            Preview (import)
          </Label>
        );
        break;
      case 'PREVIEW_DELETE':
        mode = (
          <Label color="teal" basic>
            Preview (delete)
          </Label>
        );
        break;
      default:
        mode = (
          <Label color="black" basic>
            Invalid mode
          </Label>
        );
        break;
    }
    this.setState({
      mode: mode,
    });
  };

  statusLabel = () => {
    let { data, status, isLoading } = this.state;
    !data
      ? (status = <Label color="grey">Fetching status</Label>)
      : isLoading
      ? (status = (
          <Label color="blue">
            <Icon loading name="circle notch" /> Importing literature
          </Label>
        ))
      : data.status === 'SUCCEEDED'
      ? (status = <Label color="green">Import successfull</Label>)
      : data.status === 'CANCELLED'
      ? (status = <Label color="yellow">Import cancelled</Label>)
      : (status = <Label color="red">Import failed</Label>);
    this.setState({
      status: status,
    });
  };

  calculateStatistics = () => {
    let { statistics, data, selectedResult } = this.state;

    const dataClone = Array.from(data.records);
    const newRecords = dataClone.slice(this.lastIndex, dataClone.length);

    this.lastIndex += newRecords.length;
    statistics.records.value = data.loaded_entries + '/' + data.entries_count;

    let tempRecords = [];

    for (const statistic in statistics) {
      tempRecords = newRecords.filter(record =>
        statistics[statistic].filterFunction(record)
      );
      statistics[statistic].filteredRecords = statistics[
        statistic
      ].filteredRecords.concat(tempRecords);
      if (statistic !== 'records') {
        statistics[statistic].value =
          statistics[statistic].filteredRecords.length;
      }
    }
    this.setState({
      statistics: statistics,
    });
    this.currentFilterResults(selectedResult);
  };

  currentFilterResults(key) {
    const { statistics } = this.state;
    this.setState({
      selectedResult: key,
      currentFilteredRecords: statistics[key].filteredRecords,
    });
  }

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
    const { data } = this.state;
    return (
      <>
        <Button
          className="default-margin-top"
          labelPosition="left"
          icon="left arrow"
          content="Import other files"
          loading={!data}
          disabled={!data}
          as={Link}
          to={CdsBackOfficeRoutes.importerCreate}
        />
        {this.renderCancelButton()}
      </>
    );
  };

  renderStatistics = () => {
    const { statistics, selectedResult } = this.state;
    return (
      <Statistic.Group widths="seven">
        {Object.keys(statistics).map(function(statistic, index) {
          return (
            <Statistic
              className={
                selectedResult === statistic
                  ? 'import-statistic statistic-selected'
                  : 'import-statistic'
              }
              key={statistic}
              onClick={() => this.currentFilterResults(statistic)}
            >
              <Statistic.Value>{statistics[statistic].value}</Statistic.Value>
              <Statistic.Label>{statistics[statistic].text}</Statistic.Label>
            </Statistic>
          );
        }, this)}
      </Statistic.Group>
    );
  };

  renderCancelButton = () => {
    const { data } = this.state;
    const { taskId } = this.props;
    const isRunning = !_isEmpty(data) && data.status === 'RUNNING';

    return isRunning ? (
      <>
        <CancelImportTask logId={taskId} /> <Icon loading name="circle notch" />
        This may take a while. You may leave the page, the process will continue
        in background.
      </>
    ) : null;
  };

  render() {
    const {
      data,
      mode,
      importCompleted,
      status,
      currentFilteredRecords,
    } = this.state;
    return (
      <>
        {this.renderImportReportHeader()}
        {!_isEmpty(data) && data.status !== 'FAILED' ? (
          <>
            <Segment>
              {!_isEmpty(data) ? (
                (data.loaded_entries || data.loaded_entries === 0) &&
                data.entries_count ? (
                  <Grid className="middle aligned">
                    <Grid.Column width={3}>
                      <Segment>
                        Mode: {mode}
                        <Divider />
                        Status: {status}
                      </Segment>
                    </Grid.Column>
                    <Grid.Column width={13}>
                      {this.renderStatistics()}
                    </Grid.Column>
                  </Grid>
                ) : (
                  <span>Processing file...</span>
                )
              ) : null}
            </Segment>
            {!_isEmpty(currentFilteredRecords) ? (
              <ImportedTable records={currentFilteredRecords} />
            ) : (
              importCompleted && (
                <Message>
                  <Message.Header>No records found.</Message.Header>
                  <p>No records found with the selected filter.</p>
                </Message>
              )
            )}
          </>
        ) : !_isEmpty(data) && data.status === 'FAILED' ? (
          this.renderErrorMessage(data)
        ) : null}
      </>
    );
  }
}

ImportedDocuments.propTypes = {
  taskId: PropTypes.string.isRequired,
};
