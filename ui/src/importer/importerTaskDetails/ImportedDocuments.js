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
import { ImportedDocumentReport } from './ImportedDocumentReport';
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
      const knownEntries = _get(data, 'records', []);
      const response = await importerApi.check(taskId, nextEntry);
      const responseData = response.data;
      if (responseData) {
        responseData.records = knownEntries.concat(
          _get(responseData, 'records', [])
        );
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
    } else {
      this.intervalId && clearInterval(this.intervalId);
    }
  };

  renderErrorMessage = data => {
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

  renderResultsHeader = () => {
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
        <Divider hidden />
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
        ) : (
          <>
            <Icon name="times circle" color="red" aria-label="Failed" />
            Literature import failed.
          </>
        )}
      </>
    );
  };

  handlePaginationChange = (e, { activePage }) => this.setState({ activePage });

  renderResultsContent = () => {
    const { data, activePage } = this.state;
    console.log(data.records[6]);
    return (
      <Table styled fluid striped celled structured>
        <Table.Header className="sticky-table-header">
          <Table.Row>
            <Table.HeaderCell collapsing rowspan="3" textAlign="center">
              No
            </Table.HeaderCell>
            <Table.HeaderCell width="6" rowspan="3">
              Title [Provider recid]
            </Table.HeaderCell>

            <Table.HeaderCell width="1" rowspan="3">
              Action
            </Table.HeaderCell>
            <Table.HeaderCell width="1" rowspan="3">
              Output document
            </Table.HeaderCell>
            <Table.HeaderCell colspan="4">Dependent records</Table.HeaderCell>
            <Table.HeaderCell rowspan="3">Partial matches</Table.HeaderCell>
            <Table.HeaderCell rowspan="3">Error</Table.HeaderCell>
          </Table.Row>
          <Table.Row>
            <Table.HeaderCell colspan="2">E-item</Table.HeaderCell>
            <Table.HeaderCell colspan="2">Serials</Table.HeaderCell>
          </Table.Row>
          <Table.Row>
            <Table.HeaderCell collapsing>Detected</Table.HeaderCell>
            <Table.HeaderCell width="1">Action and details</Table.HeaderCell>
            <Table.HeaderCell collapsing>Detected</Table.HeaderCell>
            <Table.HeaderCell width="1">Details</Table.HeaderCell>
          </Table.Row>
        </Table.Header>
        {data.records
          .slice((activePage - 1) * 20, (activePage - 1) * 20 + 20)
          .map((elem, index) => {
            return (
              !_isEmpty(elem) && (
                <ImportedDocumentReport
                  documentReport={elem}
                  listIndex={index + (activePage - 1) * 20}
                />
              )
            );
          })}

        <Table.Footer>
          <Table.Row>
            <Table.HeaderCell colspan="10">
              <Pagination
                defaultActivePage={1}
                totalPages={Math.floor(data.records.length / 20)}
                activePage={activePage}
                onPageChange={this.handlePaginationChange}
                floated="right"
              />
            </Table.HeaderCell>
          </Table.Row>
        </Table.Footer>
      </Table>
    );
  };

  render() {
    const { data } = this.state;
    return (
      <>
        {this.renderResultsHeader()}
        {!_isEmpty(data) && data.status !== 'FAILED' ? (
          <>
            <Header as="h2">Literature</Header>
            {!_isEmpty(data) ? (
              (data.loaded_entries || data.loaded_entries === 0) &&
              data.entries_count ? (
                <p>
                  {'Processed ' +
                    data.loaded_entries +
                    ' records out of ' +
                    data.entries_count +
                    '.'}
                </p>
              ) : (
                <p>Processing file...</p>
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
