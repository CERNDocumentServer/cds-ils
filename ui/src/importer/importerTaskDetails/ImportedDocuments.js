import React from 'react';
import PropTypes from 'prop-types';
import {
  Accordion,
  Button,
  Divider,
  Header,
  Icon,
  Message,
} from 'semantic-ui-react';
import _isEmpty from 'lodash/isEmpty';
import _get from 'lodash/get';
import { CdsBackOfficeRoutes } from '../../overridden/routes/BackofficeUrls';
import { ReportDetails } from './ReportDetails';
import { Link } from 'react-router-dom';
import { BackOfficeRoutes } from '@inveniosoftware/react-invenio-app-ils';
import { DocumentIcon } from '@inveniosoftware/react-invenio-app-ils';
import { importerApi } from '../../api/importer';
import { invenioConfig } from '@inveniosoftware/react-invenio-app-ils';

export class ImportedDocuments extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      activeIndex: -1,
      importCompleted: false,
      data: null,
      isLoading: true,
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

  handleClick = (e, titleProps) => {
    const { index } = titleProps;
    const { activeIndex } = this.state;
    const newIndex = activeIndex === index ? -1 : index;

    this.setState({ activeIndex: newIndex });
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

  renderResultsContent = () => {
    const { data, activeIndex } = this.state;
    return (
      <Accordion className="importer" styled fluid>
        {data.records.map((elem, index) => {
          const importSuccess = _get(elem, 'success', null);
          const document = importSuccess
            ? elem.created_document
              ? elem.created_document
              : elem.updated_document
            : null;
          return (
            <div key={elem.index}>
              <Accordion.Title
                active={activeIndex === index}
                index={index}
                onClick={this.handleClick}
              >
                <Icon name="dropdown" />
                {!_isEmpty(document) ? (
                  <Link
                    to={BackOfficeRoutes.documentDetailsFor(document.pid)}
                    target="_blank"
                  >
                    <DocumentIcon />
                    {document.title}
                  </Link>
                ) : importSuccess ? (
                  'No document created or updated'
                ) : (
                  <span className="danger">Error on importing this record</span>
                )}
              </Accordion.Title>
              <Accordion.Content active={activeIndex === index}>
                <ReportDetails item={elem} />
              </Accordion.Content>
            </div>
          );
        })}
      </Accordion>
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
