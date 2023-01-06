import React, { Component } from "react";
import PropTypes from "prop-types";
import _isEmpty from "lodash/isEmpty";
import { Link } from "react-router-dom";
import { Button, Header, List, Modal } from "semantic-ui-react";
import { BackOfficeRoutes } from "@inveniosoftware/react-invenio-app-ils";

export default class EitemImportDetails extends Component {
  render() {
    const { eitemReport, open, modalClose } = this.props;
    return (
      <Modal onClose={modalClose} onOpen={modalClose} open={open}>
        <Modal.Header>EItem - attention required</Modal.Header>
        <Modal.Content>
          <Modal.Description>
            {!_isEmpty(eitemReport.duplicates) && (
              <>
                <Header>Duplicated e-items found</Header>
                <List>
                  {eitemReport.duplicates.map((pid) => (
                    <List.Item key={pid}>
                      <Link to={BackOfficeRoutes.eitemDetailsFor(pid)}>{pid}</Link>
                    </List.Item>
                  ))}
                </List>
              </>
            )}
            {!_isEmpty(eitemReport.deleted_eitems) && (
              <>
                <Header>EItems deleted or replaced</Header>
                <List>
                  {eitemReport.deleted_eitems.map(
                    (eitem) => `(replaced: ${eitem.pid})`
                  )}
                </List>
              </>
            )}
          </Modal.Description>
        </Modal.Content>
        <Modal.Actions>
          <Button onClick={modalClose}>Close</Button>
        </Modal.Actions>
      </Modal>
    );
  }
}

EitemImportDetails.propTypes = {
  eitemReport: PropTypes.object.isRequired,
  open: PropTypes.bool,
  modalClose: PropTypes.func.isRequired,
};

EitemImportDetails.defaultProps = {
  open: false,
};
