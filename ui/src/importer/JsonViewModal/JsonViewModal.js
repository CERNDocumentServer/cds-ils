import React, { Component } from "react";
import PropTypes from "prop-types";
import { Button, Modal } from "semantic-ui-react";
import ReactJson from "react-json-view";

export default class JsonViewModal extends Component {
  render() {
    const { title, jsonData, open, onCloseHandler } = this.props;
    return (
      <Modal onClose={onCloseHandler} onOpen={onCloseHandler} open={open}>
        <Modal.Header>{title}</Modal.Header>
        <Modal.Content>
          <Modal.Description>
            <ReactJson src={jsonData} name={null} />
          </Modal.Description>
        </Modal.Content>
        <Modal.Actions>
          <Button onClick={onCloseHandler}>Close</Button>
        </Modal.Actions>
      </Modal>
    );
  }
}

JsonViewModal.propTypes = {
  title: PropTypes.string.isRequired,
  jsonData: PropTypes.object.isRequired,
  open: PropTypes.bool.isRequired,
  onCloseHandler: PropTypes.func.isRequired,
};
