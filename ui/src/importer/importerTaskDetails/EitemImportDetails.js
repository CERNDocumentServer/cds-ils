import React, { Component } from 'react';
import PropTypes from 'prop-types';
import _isEmpty from 'lodash/isEmpty';
import { Link } from 'react-router-dom';
import { Button, Header, List, Modal } from 'semantic-ui-react';
import { BackOfficeRoutes } from '@inveniosoftware/react-invenio-app-ils';

export class EitemImportDetails extends Component {
  constructor(props) {
    super(props);
    this.state = { open: false };
  }
  render() {
    const { eitemReport } = this.props;
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
        <Modal.Header>EItem - attention required</Modal.Header>
        <Modal.Content>
          <Modal.Description>
            {!_isEmpty(eitemReport.duplicates) && (
              <>
                <Header>Duplicated e-items found</Header>
                <List>
                  {eitemReport.duplicates.map(pid => (
                    <List.Item key={pid}>
                      <Link to={BackOfficeRoutes.eitemDetailsFor(pid)}>
                        {pid}
                      </Link>
                    </List.Item>
                  ))}
                </List>
              </>
            )}
            {!_isEmpty(eitemReport.deleted_eitems) && (
              <>
                <Header>EItems deleted or replaced</Header>
                <List>
                  {eitemReport.deleted_eitems.map(pid => (
                    <List.Item key={pid}>
                      <Link to={BackOfficeRoutes.eitemDetailsFor(pid)}>
                        {pid}
                      </Link>
                    </List.Item>
                  ))}
                </List>
              </>
            )}
            {/*<ReactJson src={jsonData} name={null} />*/}
          </Modal.Description>
        </Modal.Content>
        <Modal.Actions>
          <Button onClick={() => this.setState({ open: false })}>Close</Button>
        </Modal.Actions>
      </Modal>
    );
  }
}

EitemImportDetails.propTypes = {
  eitemReport: PropTypes.object.isRequired,
};
