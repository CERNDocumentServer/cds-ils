import { BackOfficeRoutes } from '@inveniosoftware/react-invenio-app-ils';
import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';
import { Button, Header, Icon, Label, Table } from 'semantic-ui-react';
import _isEmpty from 'lodash/isEmpty';
import _get from 'lodash/get';
import { openJsonModal as openJsonModalAction } from '../JsonViewModal/actions';
import { openSeriesDetailsModal as openSeriesDetailsModalAction } from '../SeriesImportDetailsModal/actions';
import { openEitemDetailsModal as openEitemDetailsModalAction } from '../EitemImportDetailsModal/actions';

class ImportedDocumentReportComponent extends Component {
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
    const {
      documentReport,
      listIndex,
      openJsonModal,
      openSeriesDetailsModal,
      openEitemModal,
    } = this.props;
    let title;

    if (!_isEmpty(documentReport.document)) {
      let volume = _get(documentReport, 'raw_json._serial[0].volume', '');
      volume = volume ? `v. ${volume}` : '';
      title = `${documentReport.document_json.title} (${volume})
      [${documentReport.entry_recid}]`;
    } else {
      title = documentReport.entry_recid;
    }

    return (
      <Table.Row negative={!documentReport.success}>
        <Table.Cell collapsing textAlign="center">
          {listIndex}
        </Table.Cell>
        <Table.Cell>
          <Header as="h4">{title}</Header>
        </Table.Cell>
        <Table.Cell>
          {this.renderActionLabel(documentReport.action)}
          {documentReport.raw_json && (
            <Button
              icon="code"
              floated="right"
              size="mini"
              basic
              onClick={(e, { title, jsonData }) =>
                openJsonModal(
                  'Raw import JSON',
                  _get(documentReport, 'raw_json', {})
                )
              }
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

          {!_isEmpty(documentReport.document_json) && (
            <Button
              icon="code"
              floated="right"
              size="mini"
              basic
              onClick={() =>
                openJsonModal('Document JSON', documentReport.document_json)
              }
            />
          )}
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
          {!_isEmpty(documentReport.eitem) && (
            <>
              {!_isEmpty(documentReport.eitem.output_pid) && (
                <Link
                  key={documentReport.eitem.output_pid}
                  to={BackOfficeRoutes.eitemDetailsFor(
                    documentReport.eitem.output_pid
                  )}
                  target="_blank"
                >
                  {documentReport.eitem.output_pid}
                </Link>
              )}

              {!_isEmpty(_get(documentReport, 'eitem.deleted_eitems', [])) && (
                <>
                  {_get(documentReport, 'eitem.deleted_eitems').map(eitem => (
                    <Link
                      key={eitem.pid}
                      to={BackOfficeRoutes.eitemDetailsFor(eitem.pid)}
                      target="_blank"
                    >
                      {eitem.pid}
                    </Link>
                  ))}
                </>
              )}

              {(_get(documentReport, 'eitem.deleted_eitems', []).length > 1 ||
                !_isEmpty(_get(documentReport, 'eitem.duplicates', []))) && (
                <Button
                  icon="exclamation"
                  floated="right"
                  size="mini"
                  basic
                  onClick={() => openEitemModal(documentReport.eitem)}
                />
              )}
              <br />

              {this.renderActionLabel(documentReport.eitem.action)}
            </>
          )}
          <Button
            icon="code"
            floated="right"
            size="mini"
            basic
            onClick={() =>
              openJsonModal(
                'E-item JSON',
                _get(documentReport, 'eitem.json', {})
              )
            }
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
                  <Button
                    icon="code"
                    floated="right"
                    size="mini"
                    basic
                    onClick={() =>
                      openJsonModal(
                        'Series JSON',
                        _get(documentReport, 'series[0].series_json', {})
                      )
                    }
                  />
                  {!_isEmpty(documentReport.series[0].duplicates) && (
                    <Button
                      icon="exclamation"
                      floated="right"
                      size="mini"
                      basic
                      onClick={() =>
                        openSeriesDetailsModal(documentReport.series)
                      }
                    />
                  )}
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

ImportedDocumentReportComponent.propTypes = {
  documentReport: PropTypes.object.isRequired,
  listIndex: PropTypes.number.isRequired,
  openJsonModal: PropTypes.func.isRequired,
  openEitemModal: PropTypes.func.isRequired,
  openSeriesDetailsModal: PropTypes.func.isRequired,
};

const mapDispatchToProps = dispatch => ({
  openJsonModal: (title, json) => dispatch(openJsonModalAction(title, json)),
  openEitemModal: eitemReport =>
    dispatch(openEitemDetailsModalAction(eitemReport)),
  openSeriesDetailsModal: seriesReport =>
    dispatch(openSeriesDetailsModalAction(seriesReport)),
});

export const ImportedDocumentReport = connect(
  null,
  mapDispatchToProps
)(ImportedDocumentReportComponent);
