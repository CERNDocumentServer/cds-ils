import { BackOfficeRoutes } from '@inveniosoftware/react-invenio-app-ils';
import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { Link } from 'react-router-dom';
import { Button, Header, Icon, Label, Table } from 'semantic-ui-react';
import _isEmpty from 'lodash/isEmpty';
import _get from 'lodash/get';
import { JsonViewModal } from './JsonViewModal';

export class ImportedDocumentReport extends Component {
  renderActionLabel = action => {
    let color;
    if (action === 'create') {
      color = 'green';
    } else if (action === 'update' || action === 'replace') {
      color = 'yellow';
    } else {
      color = 'red';
    }
    return <Label color={color}>{action ? action : 'error'}</Label>;
  };

  render() {
    const { documentReport, listIndex } = this.props;
    // console.log(documentReport);
    return (
      <Table.Row negative={!documentReport.success}>
        <Table.Cell collapsing textAlign="center">
          {listIndex}
        </Table.Cell>
        <Table.Cell>
          <Header as="h4">
            {documentReport.document
              ? `${documentReport.document_json.title} [${documentReport.entry_recid}]`
              : documentReport.entry_recid}
          </Header>
        </Table.Cell>
        <Table.Cell>
          {this.renderActionLabel(documentReport.action)}
          {documentReport.raw_json && (
            <JsonViewModal
              title="Raw import JSON"
              jsonData={_get(documentReport, 'raw_json', {})}
            />
          )}
        </Table.Cell>
        <Table.Cell>
          {documentReport.output_pid ? (
            <Link
              to={BackOfficeRoutes.documentDetailsFor(
                documentReport.output_pid
              )}
              target="_blank"
            >
              {documentReport.output_pid}
            </Link>
          ) : (
            '-'
          )}
          <JsonViewModal
            title="Document JSON"
            jsonData={documentReport.document_json}
          />
        </Table.Cell>
        <Table.Cell collapsing textAlign="center">
          {!_isEmpty(documentReport.eitem) && (
            <>
              {' '}
              <Icon color="green" name="checkmark" size="large" />
            </>
          )}
        </Table.Cell>
        <Table.Cell>
          {!_isEmpty(documentReport.eitem) &&
            this.renderActionLabel(documentReport.eitem.action)}
          {!_isEmpty(_get(documentReport, 'eitem.deleted_eitems')) && (
            <>
              {_get(documentReport, 'eitem.deleted_eitems').map(pid => (
                <Link
                  key={pid}
                  to={BackOfficeRoutes.documentDetailsFor(pid)}
                  target="_blank"
                >
                  {pid}
                </Link>
              ))}
            </>
          )}
          <JsonViewModal
            title="E-item JSON"
            jsonData={_get(documentReport, 'eitem.json', {})}
          />
        </Table.Cell>
        <Table.Cell collapsing textAlign="center">
          {!_isEmpty(documentReport.series) && (
            <>
              {' '}
              <Icon color="green" name="checkmark" size="large" />
              <Label circular>{documentReport.series.length}</Label>
            </>
          )}
        </Table.Cell>
        <Table.Cell>
          {!_isEmpty(documentReport.series) && (
            <>
              {' '}
              {documentReport.series.length === 1 && (
                <>
                  {documentReport.series[0].output_pid && (
                    <>
                      {' '}
                      <Link
                        to={BackOfficeRoutes.seriesDetailsFor(
                          documentReport.series[0].output_pid
                        )}
                        target="_blank"
                      >
                        {documentReport.series[0].output_pid}
                      </Link>
                      <br />
                    </>
                  )}{' '}
                  {this.renderActionLabel(documentReport.series[0].action)}{' '}
                  {!_isEmpty(documentReport.series[0].duplicates) && (
                    <Icon color="red" name="exclamation" size="large" />
                  )}
                  <JsonViewModal
                    title="Series JSON"
                    jsonData={_get(documentReport, 'series[0].series_json', {})}
                  />
                </>
              )}
            </>
          )}
        </Table.Cell>
        <Table.Cell>
          {!_isEmpty(documentReport.partial_matches) && (
            <>
              {' '}
              <Icon color="red" name="exclamation" size="large" />
              {documentReport.partial_matches.map(entry => {
                return (
                  <>
                    {
                      <Link
                        to={BackOfficeRoutes.documentDetailsFor(entry.pid)}
                        target="_blank"
                      >
                        {entry.pid}
                      </Link>
                    }{' '}
                    <Label>{entry.type}</Label>
                  </>
                );
              })}
            </>
          )}
        </Table.Cell>
        <Table.Cell>
          {!_isEmpty(documentReport.error) && (
            <>
              {' '}
              <Icon color="red" name="exclamation" size="large" />
              {documentReport.error}
            </>
          )}
        </Table.Cell>
      </Table.Row>
    );
  }
}

ImportedDocumentReport.propTypes = {
  documentReport: PropTypes.object.isRequired,
  listIndex: PropTypes.number.isRequired,
};
