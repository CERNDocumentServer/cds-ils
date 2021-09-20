import React from 'react';
import PropTypes from 'prop-types';
import {
  Button,
  Divider,
  Icon,
  Message,
  Segment,
  Statistic,
  Label,
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
      filteredRecords: [],
      isLoading: true,
      statistics: [],
    };
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
          data: response.data,
          filteredRecords: response.data.records,
        });
      } else {
        this.setState({
          isLoading: true,
          data: response.data,
          filteredRecords: response.data.records,
        });
      }
      this.calculateStatistics(response.data);
    } else {
      this.intervalId && clearInterval(this.intervalId);
    }
  };

  calculateStatistics = data => {
    const importStatistics = [];
    importStatistics.push({
      text: 'Mode',
      value: <Label>{data.mode}</Label>,
    });
    importStatistics.push({
      text: 'Records',
      value: data.loaded_entries + '/' + data.entries_count,
      filter: 'Reset Filter',
      fnc: a => a,
    });
    importStatistics.push({
      text: 'Records created',
      value: data.records.filter(record => record.action === 'create').length,
      filter: 'Filter',
      fnc: a => a.action === 'create',
    });
    importStatistics.push({
      text: 'Records updated',
      value: data.records.filter(record => record.action === 'update').length,
      filter: 'Filter',
      fnc: a => a.action === 'update',
    });
    importStatistics.push({
      text: 'Records with errors',
      value: data.records.filter(record => _isNull(record.action)).length,
      filter: 'Filter',
      fnc: a => _isNull(a.action),
    });
    importStatistics.push({
      text: 'Records with eItem',
      value: data.records.filter(record => !_isNull(record.eitem)).length,
      filter: 'Filter',
      fnc: a => !_isNull(a.eitem),
    });
    importStatistics.push({
      text: 'Records with Serials',
      value: data.records.filter(record => !_isEmpty(record.series)).length,
      filter: 'Filter',
      fnc: a => !_isEmpty(a.series),
    });
    this.setState({
      statistics: importStatistics,
    });
  };

  filterResults(fnc) {
    const { data } = this.state;
    const newFilteredRecords = data.records.filter(record => fnc(record));
    this.setState({ filteredRecords: newFilteredRecords });
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
    const { data, isLoading } = this.state;
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
        <Divider />
        {!data ? (
          <>
            <Icon loading name="circle notch" />
            Fetching status...
          </>
        ) : isLoading ? (
          <>
            <Icon name="circle notch" loading aria-label="Import in progress" />
            Importing literature... This may take a while. You may leave the
            page, the process will continue in background.
          </>
        ) : data.status === 'SUCCEEDED' ? (
          <>
            <Icon name="check circle" color="green" aria-label="Completed" />
            Literature imported successfully.
          </>
        ) : data.status === 'CANCELLED' ? (
          <>
            <Icon name="times circle" color="yellow" aria-label="Cancelled" />
            Literature import was cancelled by the user.
          </>
        ) : (
          <>
            <Icon name="exclamation circle" color="red" aria-label="Failed" />
            Literature import failed.
          </>
        )}
        <Divider />
      </>
    );
  };

  renderStatistics = () => {
    const { statistics } = this.state;

    return (
      <Statistic.Group widths="seven">
        {statistics.map(function(statistic) {
          return (
            <Statistic key={statistic.text}>
              <Statistic.Value>{statistic.value}</Statistic.Value>
              <Statistic.Label>{statistic.text}</Statistic.Label>
              {statistic.filter && (
                <Button onClick={() => this.filterResults(statistic.fnc)}>
                  {statistic.filter}
                </Button>
              )}
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

    return isRunning ? <CancelImportTask logId={taskId} /> : null;
  };

  render() {
    const { data, filteredRecords, statistics } = this.state;
    return (
      <>
        {this.renderImportReportHeader()}
        {!_isEmpty(data) && data.status !== 'FAILED' ? (
          <>
            <Segment>
              {!_isEmpty(data) ? (
                (data.loaded_entries || data.loaded_entries === 0) &&
                data.entries_count ? (
                  <div>
                    {_isEmpty(statistics.length) && this.renderStatistics()}
                  </div>
                ) : (
                  <span>Processing file...</span>
                )
              ) : null}
            </Segment>
            {!_isEmpty(data.records) ? (
              <ImportedTable records={filteredRecords} />
            ) : null}
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
