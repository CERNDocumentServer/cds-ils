import _get from 'lodash/get';
import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { Link } from 'react-router-dom';
import { Button, Header, Modal, Table } from 'semantic-ui-react';
import { BackOfficeRoutes } from '@inveniosoftware/react-invenio-app-ils';
import { JsonViewModal } from './JsonViewModal';

export class SeriesImportDetails extends Component {
  constructor(props) {
    super(props);
    this.state = { open: false };
  }
  render() {
    const { seriesReport } = this.props;
    const { open } = this.state;
    return (
      <Modal
        onClose={() => this.setState({ open: false })}
        onOpen={() => this.setState({ open: true })}
        open={open}
        trigger={
          <Button
            color="red"
            icon="exclamation"
            floated="right"
            size="mini"
            basic
          />
        }
      >
        <Modal.Header>Series - attention required</Modal.Header>
        <Modal.Content>
          <Modal.Description>
            <Header>Duplicated series found</Header>
            <Table styled fluid striped celled structured>
              {seriesReport.map(series => {
                return (
                  <Table.Row key={series.output_pid}>
                    <Table.Cell>
                      {series.series_json.title}
                      <JsonViewModal
                        title="Series JSON"
                        jsonData={_get(series, 'series_json', {})}
                      />
                    </Table.Cell>
                    {series.duplicates.map(pid => (
                      <>
                        <Link
                          key={pid}
                          to={BackOfficeRoutes.eitemDetailsFor(pid)}
                        >
                          {pid}
                        </Link>
                        {', '}
                      </>
                    ))}
                  </Table.Row>
                );
              })}
            </Table>
          </Modal.Description>
        </Modal.Content>
        <Modal.Actions>
          <Button onClick={() => this.setState({ open: false })}>Close</Button>
        </Modal.Actions>
      </Modal>
    );
  }
}

SeriesImportDetails.propTypes = {
  seriesReport: PropTypes.object.isRequired,
};
