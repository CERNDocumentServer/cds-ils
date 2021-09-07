import React from 'react';
import PropTypes from 'prop-types';
import {
  Button,
  Divider,
  Header,
  Icon,
  Message,
  Pagination,
  Table,
} from 'semantic-ui-react';
import _isEmpty from 'lodash/isEmpty';
import _get from 'lodash/get';
import { CancelImportTask } from './cancelImportTask';
import { EitemImportDetailsModal } from '../EitemImportDetailsModal';
import { SeriesImportDetailsModal } from '../SeriesImportDetailsModal';
import { JsonViewModal } from '../JsonViewModal';
import { modeFormatter } from '../ImporterList';
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
      isLoading: true,
      activePage: 1,
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
    } else {
      this.intervalId && clearInterval(this.intervalId);
    }
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
    const { data } = this.state;
    return (
      <>
        {this.renderImportReportHeader()}
        {!_isEmpty(data) && data.status !== 'FAILED' ? (
          <>
            <Header as="h3">Import report</Header>
            {modeFormatter(data.mode)}{' '}
            {!_isEmpty(data) ? (
              (data.loaded_entries || data.loaded_entries === 0) &&
              data.entries_count ? (
                <span>
                  {'Processed ' +
                    data.loaded_entries +
                    ' records out of ' +
                    data.entries_count +
                    '.'}
                </span>
              ) : (
                <span>Processing file...</span>
              )
            ) : null}
            {!_isEmpty(data.records) ? this.renderResultsContent() : null}
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
