import React, { Component } from "react";
import PropTypes from "prop-types";
import { Button, Confirm, Message } from "semantic-ui-react";
import { importerApi } from "../../../api/importer";
import { withCancel } from "@inveniosoftware/react-invenio-app-ils";

export class CancelImportTask extends Component {
  constructor(props) {
    super(props);
    this.state = {
      modalOpen: false,
      cancelFailed: false,
      cancelLoading: false,
      taskCancelled: undefined,
    };
  }

  handleCancelImportAction = async () => {
    const { logId } = this.props;
    try {
      this.setState({ cancelLoading: true });
      const cancellableImportCancelAction = withCancel(importerApi.cancel(logId));
      await cancellableImportCancelAction.promise;
      this.setState({
        cancelLoading: false,
        modalOpen: false,
        cancelFailed: false,
        taskCancelled: true,
      });
    } catch (error) {
      this.setState({
        cancelLoading: false,
        cancelFailed: true,
        modalOpen: false,
      });
    }
  };

  handleCloseModal = () => {
    this.setState({ modalOpen: false });
  };

  handleOpenModal = () => {
    this.setState({ modalOpen: true });
  };

  render() {
    const { modalOpen, cancelLoading, cancelFailed, taskCancelled } = this.state;
    return (
      <>
        {cancelFailed && (
          <Message negative>
            <Message.Header>Import cancel action failed.</Message.Header>
            <p>
              Try again later. If the problem persists, contact the technical support.
            </p>
          </Message>
        )}
        {taskCancelled && (
          <Message positive>
            <Message.Header>The import was cancelled successfully</Message.Header>
          </Message>
        )}
        <Button color="red" content="Cancel import" onClick={this.handleOpenModal} />{" "}
        <Confirm
          open={modalOpen}
          onCancel={this.handleCloseModal}
          onConfirm={this.handleCancelImportAction}
          header="Confirm cancel action"
          content="You are about to cancel current import - the cancel will be
          performed after the current record is processed.
          Are you sure you want to proceed?"
          loading={cancelLoading}
        />
      </>
    );
  }
}

CancelImportTask.propTypes = {
  logId: PropTypes.number.isRequired,
};
