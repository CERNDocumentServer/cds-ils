import _get from "lodash/get";
import React, { Component } from "react";
import PropTypes from "prop-types";
import { Link } from "react-router-dom";
import { Button, Header, Modal, Table } from "semantic-ui-react";
import { BackOfficeRoutes } from "@inveniosoftware/react-invenio-app-ils";

export default class SeriesImportDetails extends Component {
  render() {
    const { seriesReport, open, modalClose, openJsonModal } = this.props;
    return (
      <Modal onClose={modalClose} onOpen={modalClose} open={open}>
        <Modal.Header>Series - attention required</Modal.Header>
        <Modal.Content>
          <Modal.Description>
            <Header>Duplicated series found</Header>
            <Table styled fluid striped celled structured>
              {seriesReport.map((series) => {
                return (
                  <Table.Row key={series.output_pid}>
                    <Table.Cell>
                      {series.series_json.title}
                      <Button
                        onClick={() =>
                          openJsonModal("Series JSON", _get(series, "series_json", {}))
                        }
                      />
                    </Table.Cell>
                    {series.duplicates.map((pid) => (
                      <>
                        <Link key={pid} to={BackOfficeRoutes.seriesDetailsFor(pid)}>
                          {pid}
                        </Link>
                        {", "}
                      </>
                    ))}
                  </Table.Row>
                );
              })}
            </Table>
          </Modal.Description>
        </Modal.Content>
        <Modal.Actions>
          <Button onClick={modalClose}>Close</Button>
        </Modal.Actions>
      </Modal>
    );
  }
}

SeriesImportDetails.propTypes = {
  seriesReport: PropTypes.object.isRequired,
  open: PropTypes.bool.isRequired,
  modalClose: PropTypes.func.isRequired,
  openJsonModal: PropTypes.func.isRequired,
};
