import React, { Component } from 'react';
import { Link } from 'react-router-dom';
import {
  Container,
  Header,
  Segment,
  Button,
  Form,
  Modal,
  Icon,
  Label,
  Message,
  Divider,
  Grid,
} from 'semantic-ui-react';
import {
  ResultsTable,
  invenioConfig,
  history,
  withCancel,
} from '@inveniosoftware/react-invenio-app-ils';
import { BackOfficeRouteGenerators } from '../../routes/BackofficeUrls';
import _isEmpty from 'lodash/isEmpty';
import _get from 'lodash/get';
import { importerApi } from '../../api/importer';
import { Loader } from 'semantic-ui-react';
import { DateTime } from 'luxon';

class ImporterList extends Component {
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

  modeFormatter = ({ col, row }) => {
    switch (row[col.field]) {
      case 'CREATE':
        return (
          <Label color="blue" basic>
            <Icon name="plus" />
            Create
          </Label>
        );
      case 'DELETE':
        return (
          <Label color="red" basic>
            <Icon name="minus" />
            Delete
          </Label>
        );
      default:
        return null;
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
      title: 'Literatures in file',
      field: 'total_entries',
      formatter: this.optionalFormatter,
    },
    { title: 'Provider', field: 'provider', formatter: this.labelFormatter },
    { title: 'Mode', field: 'mode', formatter: this.modeFormatter },
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
          data={data.results}
          columns={this.columns}
          renderEmptyResultsElement={() => this.emptyMessage}
        />
        {!_isEmpty(data.results) && (
          <Grid>
            <Grid.Column width={16} textAlign="center">
              Showing the last {data.results.length} rows.
            </Grid.Column>
          </Grid>
        )}
      </>
    );
  }
}

export class Importer extends Component {
  constructor(props) {
    super(props);
    this.filesRef = React.createRef();
    this.state = {
      provider: '',
      mode: '',
      file: null,
      openModal: false,
      providerMissing: false,
      modeMissing: false,
      fileMissing: false,
      error: {},
    };
  }

  handleChange = (e, { name, value }) =>
    this.setState({
      [name]: value,
      providerMissing: false,
      modeMissing: false,
      fileMissing: false,
    });

  postData = async formData => {
    try {
      const response = await importerApi.createTask(formData);

      const taskId = response.data.id;
      history.push(BackOfficeRouteGenerators.importerDetailsFor(taskId));
    } catch (error) {
      console.error(error);
      this.setState({
        error: error,
      });
    }
  };

  handleSubmit = () => {
    const { provider, mode, file } = this.state;
    if (!_isEmpty(provider) && !_isEmpty(mode) && file) {
      const formData = new FormData();
      formData.append('provider', provider);
      formData.append('mode', mode);
      formData.append('file', file);
      this.postData(formData);
    } else {
      if (_isEmpty(provider)) {
        this.setState({ providerMissing: true });
      }
      if (_isEmpty(mode)) {
        this.setState({ modeMissing: true });
      }
      if (!file) {
        this.setState({ fileMissing: true });
      }
    }
  };

  onFileChange = event => {
    const file = this.filesRef.current.files[0];
    this.setState({
      file: file,
      providerMissing: false,
      modeMissing: false,
      fileMissing: false,
    });
  };

  renderErrorMessage = error => {
    const message = _get(error, 'response.data.message');
    return (
      <Message negative>
        <Message.Header>Something went wrong</Message.Header>
        <p>{message}</p>
      </Message>
    );
  };

  renderModal = () => {
    const { openModal } = this.state;

    return (
      <Modal
        onClose={() => this.setState({ openModal: false })}
        onOpen={() => this.setState({ openModal: true })}
        open={openModal}
        size="small"
        trigger={<Button primary>Import</Button>}
      >
        <Header>Deleting Records</Header>
        <Modal.Content>
          <p>Are you sure you want to delete records?</p>
        </Modal.Content>
        <Modal.Actions>
          <Button
            color="red"
            onClick={() => this.setState({ openModal: false })}
          >
            <Icon name="remove" /> No
          </Button>
          <Button
            primary
            onClick={() => {
              this.setState({ openModal: false });
              this.handleSubmit();
            }}
          >
            <Icon name="checkmark" /> Yes
          </Button>
        </Modal.Actions>
      </Modal>
    );
  };

  renderForm = () => {
    const {
      provider,
      mode,
      file,
      providerMissing,
      modeMissing,
      fileMissing,
    } = this.state;
    return (
      <Form onSubmit={mode !== 'delete' ? this.handleSubmit : null}>
        <Segment>
          <Form.Group widths="equal">
            <Form.Select
              placeholder="Select a provider ..."
              label="Provider"
              search
              selection
              name="provider"
              value={provider}
              options={invenioConfig.IMPORTER.providers}
              onChange={this.handleChange}
              required
              error={providerMissing ? 'Please enter a provider' : null}
            />
            <Form.Select
              placeholder="Select a mode ..."
              label="Mode"
              search
              selection
              name="mode"
              value={mode}
              options={invenioConfig.IMPORTER.modes}
              onChange={this.handleChange}
              required
              error={modeMissing ? 'Please enter a mode' : null}
            />
          </Form.Group>
          <Form.Group widths="equal">
            <Form.Field className="default-margin-top">
              <Button
                icon="file"
                content="Choose File"
                labelPosition="left"
                onClick={e => {
                  e.preventDefault();
                  this.filesRef.current.click();
                }}
              />
              <input
                hidden
                ref={this.filesRef}
                id="upload"
                type="file"
                accept=".xml"
                onChange={this.onFileChange}
              />
              <Label basic prompt={fileMissing} pointing="left">
                {file ? file.name : 'No file selected.'}
              </Label>
            </Form.Field>
          </Form.Group>
        </Segment>
        {mode === 'delete' ? (
          this.renderModal()
        ) : (
          <Form.Button primary content="Import" />
        )}
      </Form>
    );
  };

  render() {
    const { error } = this.state;
    return (
      <Container id="importer" className="spaced">
        <Header as="h2">Literatures Importer</Header>
        <Header as="h3">Import from a file</Header>
        <p>
          {!_isEmpty(error)
            ? 'Fill in the form below to import literatures.'
            : null}
        </p>
        {!_isEmpty(error) ? this.renderErrorMessage(error) : null}
        {this.renderForm()}

        <Divider />

        <Header as="h3">Previous imports</Header>
        <ImporterList />
      </Container>
    );
  }
}
