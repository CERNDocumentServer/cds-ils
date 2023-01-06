import React, { Component } from "react";
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
  Table,
} from "semantic-ui-react";
import { invenioConfig, history } from "@inveniosoftware/react-invenio-app-ils";
import { ImporterList } from "./ImporterList";
import { BackOfficeRouteGenerators } from "../overridden/routes/BackofficeUrls";
import _isEmpty from "lodash/isEmpty";
import _get from "lodash/get";
import { importerApi } from "../api/importer";

export class Importer extends Component {
  constructor(props) {
    super(props);
    this.filesRef = React.createRef();
    this.state = {
      provider: "",
      ignoreMissingRules: false,
      mode: "",
      file: null,
      openModal: false,
      providerMissing: false,
      modeMissing: false,
      fileMissing: false,
      error: {},
      confirmImportOpen: false,
      submitIsLoading: false,
    };
  }

  handleChange = (e, { name, value }) => {
    this.setState({
      [name]: value,
    });
  };

  handleCheckboxChange = (e, { name, checked }) => {
    this.setState({
      [name]: checked,
    });
  };

  handleModalOpen = () => this.setState({ openModal: true });
  handleModalClose = () => this.setState({ openModal: false });

  postData = async (formData) => {
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

  handleSubmit = (action) => {
    const { provider, mode, file, ignoreMissingRules } = this.state;
    this.setState({ submitIsLoading: true });
    let importMode = mode;
    if (action === "PREVIEW" && mode === "IMPORT") {
      importMode = "PREVIEW_IMPORT";
    } else if (action === "PREVIEW" && mode === "DELETE") {
      importMode = "PREVIEW_DELETE";
    }

    if (!_isEmpty(provider) && !_isEmpty(mode) && file) {
      const formData = new FormData();
      formData.append("provider", provider);
      formData.append("mode", importMode);
      formData.append("file", file);
      formData.append("ignore_missing_rules", ignoreMissingRules);
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
      this.handleImportConfirmClose();
      this.setState({ submitIsLoading: false });
    }
  };

  onFileChange = (event) => {
    const file = this.filesRef.current.files[0];
    this.setState({
      file: file,
    });
  };

  renderErrorMessage = (error) => {
    const message = _get(error, "response.data.message");
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
        onClose={this.handleModalClose}
        onOpen={this.handleModalOpen}
        open={openModal}
        size="small"
        trigger={<Button secondary>Import</Button>}
      >
        <Header>Deleting Records</Header>
        <Modal.Content>
          <p>Are you sure you want to delete records?</p>
        </Modal.Content>
        <Modal.Actions>
          <Button color="red" onClick={this.handleModalClose}>
            <Icon name="remove" /> No
          </Button>
          <Button
            primary
            action="DELETE"
            onClick={() => {
              this.handleModalClose();
              this.handleSubmit("DELETE");
            }}
          >
            <Icon name="checkmark" /> Yes
          </Button>
        </Modal.Actions>
      </Modal>
    );
  };

  handleImportConfirmOpen = () => this.setState({ confirmImportOpen: true });
  handleImportConfirmClose = () => this.setState({ confirmImportOpen: false });

  renderImportConfirm = () => {
    const {
      confirmImportOpen,
      provider,
      mode,
      file,
      ignoreMissingRules,
      submitIsLoading,
    } = this.state;

    return (
      <Modal
        open={confirmImportOpen}
        onOpen={this.handleImportConfirmOpen}
        onClose={this.handleImportConfirmClose}
      >
        <Modal.Header>Confirm import parameters</Modal.Header>
        <Modal.Content>
          <Header as="h4">You are about to import records, using parameters:</Header>
          <Table>
            <Table.Body>
              <Table.Row>
                <Table.Cell width="6">Provider</Table.Cell>
                <Table.Cell negative={!provider}>{provider}</Table.Cell>
              </Table.Row>
              <Table.Row>
                <Table.Cell>Mode</Table.Cell>
                <Table.Cell negative={!mode}>
                  {mode && <Label>{mode}</Label>}
                </Table.Cell>
              </Table.Row>
              <Table.Row>
                <Table.Cell>File name</Table.Cell>
                <Table.Cell negative={!file}>{file?.name}</Table.Cell>
              </Table.Row>
              <Table.Row>
                <Table.Cell>Strict JSON rules</Table.Cell>
                <Table.Cell>
                  {!ignoreMissingRules ? (
                    <Icon name="checkmark box" color="green" />
                  ) : (
                    <Icon name="close" color="red" />
                  )}
                </Table.Cell>
              </Table.Row>
            </Table.Body>
          </Table>
          <Header as="h4">Are you sure you want to proceed?</Header>
        </Modal.Content>
        <Modal.Actions>
          <Button onClick={this.handleImportConfirmClose}>Cancel</Button>
          <Button
            primary
            disabled={!mode || !provider || !file}
            loading={submitIsLoading}
            onClick={() => {
              this.handleSubmit("IMPORT");
            }}
          >
            Confirm
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
      ignoreMissingRules,
      providerMissing,
      modeMissing,
      fileMissing,
    } = this.state;

    return (
      <Form>
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
              error={providerMissing ? "Please enter a provider" : null}
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
              error={modeMissing ? "Please enter a mode" : null}
            />
          </Form.Group>
          <Form.Group widths="equal">
            <Form.Checkbox
              className="default-margin-top"
              label="Ignore missing import rules"
              checked={ignoreMissingRules}
              name="ignoreMissingRules"
              onChange={this.handleCheckboxChange}
            />
            <Form.Field className="default-margin-top">
              <Button
                icon="file"
                content="Choose File"
                labelPosition="left"
                onClick={(e) => {
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
                {file ? file.name : "No file selected."}
              </Label>
            </Form.Field>
          </Form.Group>
        </Segment>
        <>
          <Button
            primary
            onClick={() => this.handleSubmit("PREVIEW")}
            content="Preview"
          />
          {mode === "DELETE" ? (
            this.renderModal()
          ) : (
            <>
              <Button
                secondary
                content="Import"
                onClick={(e, props) => {
                  this.handleImportConfirmOpen();
                }}
              />
              {this.renderImportConfirm()}
            </>
          )}
        </>
      </Form>
    );
  };

  render() {
    const { error } = this.state;
    return (
      <Container id="importer" fluid>
        <Header as="h2">Literature Importer</Header>
        <Container>
          <Header as="h3">Import from a file</Header>
          <p>
            {!_isEmpty(error) ? "Fill in the form below to import literature." : null}
          </p>
          {!_isEmpty(error) ? this.renderErrorMessage(error) : null}
          {this.renderForm()}
        </Container>
        <Divider section />

        <Header as="h3">Previous imports</Header>
        <ImporterList />
      </Container>
    );
  }
}
