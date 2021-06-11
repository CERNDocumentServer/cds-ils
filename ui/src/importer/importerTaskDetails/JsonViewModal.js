import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { Button, Header, Modal } from 'semantic-ui-react';
import ReactJson from 'react-json-view';

export class JsonViewModal extends Component {
  constructor(props) {
    super(props);
    this.state = { open: false };
  }

  render() {
    const { title, jsonData } = this.props;
    const { open } = this.state;

    return (
      <Modal
        onClose={() => this.setState({ open: false })}
        onOpen={() => this.setState({ open: true })}
        open={open}
        trigger={<Button icon="code" floated="right" size="mini" basic />}
      >
        <Modal.Header>{title}</Modal.Header>
        <Modal.Content>
          <Modal.Description>
            <ReactJson src={jsonData} name={null} />
          </Modal.Description>
        </Modal.Content>
        <Modal.Actions>
          <Button onClick={() => this.setState({ open: false })}>Close</Button>
        </Modal.Actions>
      </Modal>
    );
  }
}

JsonViewModal.propTypes = {
  title: PropTypes.string.isRequired,
  jsonData: PropTypes.object.isRequired,
};
