import React from 'react';
import PropTypes from 'prop-types';
import {
  Button,
  Divider,
  Icon,
  Message,
  Pagination,
  Table,
  Segment,
} from 'semantic-ui-react';
import _isEmpty from 'lodash/isEmpty';
import _isNull from 'lodash/isNull';
import _get from 'lodash/get';
import _unionWith from 'lodash/unionWith';
import isEqual from 'lodash/isEqual';
import { CancelImportTask } from './cancelImportTask';
import { EitemImportDetailsModal } from '../EitemImportDetailsModal';
import { SeriesImportDetailsModal } from '../SeriesImportDetailsModal';
import { JsonViewModal } from '../JsonViewModal';
import { ImportedDocumentReport } from './ImportedDocumentReport';
import { CdsBackOfficeRoutes } from '../../overridden/routes/BackofficeUrls';
import { Link } from 'react-router-dom';
import { importerApi } from '../../api/importer';
import { invenioConfig } from '@inveniosoftware/react-invenio-app-ils';

export class ImportedDocuments extends React.Component {
  constructor(props) {
    super(props);
    this.pageSize = 100;
    this.state = {
      importCompleted: false,
      data: null,
      importedRecords: [],
      isLoading: true,
      activePage: 1,
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
    const { importCompleted, data, importedRecords } = this.state;
    const { taskId } = this.props;
    if (!importCompleted) {
      const nextEntry = _get(data, 'loaded_entries', 0);
      const response = await importerApi.check(taskId, nextEntry);
      const responseData = response.data;

      if (responseData) {
        const updatedRecordsList = _unionWith([
          importedRecords,
          _get(responseData, 'records', []),
          isEqual,
        ]);
        this.setState({ importedRecords: updatedRecordsList });
      }
      if (response.data.status !== 'RUNNING') {
        this.setState({
          importCompleted: true,
          isLoading: false,
          data: response.data,
        });
      } else {
        this.setState({
          data: response.data,
          isLoading: true,
        });
      }
      console.log(response.data);
      this.calculateStatistics(response.data);
    } else {
      this.intervalId && clearInterval(this.intervalId);
    }
  };

  calculateStatistics = data => {
    const importStatistics = [];
    importStatistics.push({
      text: 'Mode',
      value: data.mode,
      size: 'mini',
    });
    importStatistics.push({
      text: 'Records',
      value: data.loaded_entries + '/' + data.entries_count,
    });
    importStatistics.push({
      text: 'Records created',
      value: data.records.filter(record => record.action == 'create').length,
    });
    importStatistics.push({
      text: 'Records updated',
      value: data.records.filter(record => record.action == 'update').length,
    });
    importStatistics.push({
      text: 'Records with errors',
      value: data.records.filter(record => _isNull(record.action)).length,
    });
    importStatistics.push({
      text: 'Records with eItem',
      value: data.records.filter(record => !_isNull(record.eitem)).length,
    });
    importStatistics.push({
      text: 'Records with Serials',
      value: data.records.filter(record => !_isEmpty(record.series)).length,
    });
    this.setState({
      statistics: importStatistics,
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

  handlePaginationChange = (e, { activePage }) => this.setState({ activePage });

  renderStatistics = () => {
    const { statistics } = this.state;

    return (
      <>
        <div className="ui seven statistics">
          {statistics.map(function(statistic, index) {
            return (
              <div key={index} className="statistic">
                <div className="value">{statistic.value}</div>
                <div className="label">{statistic.text}</div>
              </div>
            );
          })}
        </div>
      </>
    );
  };

  renderResultsContent = () => {
    const { data, activePage } = this.state;
    return (
      <>
        <Table styled="true" fluid="true" striped celled structured width={16}>
          <Table.Header className="sticky-table-header">
            <Table.Row>
              <Table.HeaderCell collapsing rowSpan="3" textAlign="center">
                No
              </Table.HeaderCell>
              <Table.HeaderCell width="5" rowSpan="3">
                Title [Provider recid]
              </Table.HeaderCell>

              <Table.HeaderCell collapsing rowSpan="3">
                Action
              </Table.HeaderCell>
              <Table.HeaderCell collapsing rowSpan="3">
                Output document
              </Table.HeaderCell>
              <Table.HeaderCell collapsing colSpan="4">
                Dependent records
              </Table.HeaderCell>
              <Table.HeaderCell collapsing rowSpan="3">
                Partial matches
              </Table.HeaderCell>
              <Table.HeaderCell collapsing rowSpan="3">
                Error
              </Table.HeaderCell>
            </Table.Row>
            <Table.Row>
              <Table.HeaderCell collapsing colSpan="2">
                E-item
              </Table.HeaderCell>
              <Table.HeaderCell collapsing colSpan="2">
                Serials
              </Table.HeaderCell>
            </Table.Row>
            <Table.Row>
              <Table.HeaderCell collapsing>Detected</Table.HeaderCell>
              <Table.HeaderCell collapsing>Action and details</Table.HeaderCell>
              <Table.HeaderCell collapsing>Detected</Table.HeaderCell>
              <Table.HeaderCell collapsing>Details</Table.HeaderCell>
            </Table.Row>
          </Table.Header>
          <Table.Body>
            {data.records
              .slice(
                activePage * this.pageSize - this.pageSize,
                activePage * this.pageSize
              )
              .map((elem, index) => {
                return (
                  !_isEmpty(elem) && (
                    <ImportedDocumentReport
                      key={index}
                      documentReport={elem}
                      listIndex={index + (activePage - 1) * this.pageSize + 1}
                    />
                  )
                );
              })}
          </Table.Body>

          <Table.Footer>
            <Table.Row>
              <Table.HeaderCell colSpan="10">
                <Pagination
                  defaultActivePage={1}
                  totalPages={Math.ceil(data.records.length / this.pageSize)}
                  activePage={activePage}
                  onPageChange={this.handlePaginationChange}
                  floated="right"
                />
              </Table.HeaderCell>
            </Table.Row>
          </Table.Footer>
        </Table>
        <JsonViewModal />
        <SeriesImportDetailsModal />
        <EitemImportDetailsModal />
      </>
    );
  };

  renderCancelButton = () => {
    const { data } = this.state;
    const { taskId } = this.props;

    return (
      <>
        {!_isEmpty(data) && data.status === 'RUNNING' && (
          <CancelImportTask logId={taskId} />
        )}
      </>
    );
  };

  render() {
    const { data, importedRecords, statistics } = this.state;
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

            {!_isEmpty(importedRecords) ? this.renderResultsContent() : null}
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
