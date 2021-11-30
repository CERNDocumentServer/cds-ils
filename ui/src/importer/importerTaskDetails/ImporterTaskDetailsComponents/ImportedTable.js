import React from 'react';
import PropTypes from 'prop-types';
import { Pagination, Table } from 'semantic-ui-react';
import { EitemImportDetailsModal } from '../../EitemImportDetailsModal';
import { SeriesImportDetailsModal } from '../../SeriesImportDetailsModal';
import { JsonViewModal } from '../../JsonViewModal';
import { ImportedDocumentReport } from './ImportedDocumentReport';

export class ImportedTable extends React.Component {
  constructor(props) {
    super(props);
  }

  handlePaginationChange = (e, { activePage }) => {
    const { onPageChange } = this.props;
    onPageChange(activePage);
  };

  render() {
    const { records, activePage, pageSize, totalPages } = this.props;

    return (
      <>
        <Table styled="true" fluid="true" striped celled structured width={16}>
          <Table.Header className="sticky-table-header">
            <Table.Row>
              <Table.HeaderCell collapsing rowSpan="3" textAlign="center">
                No
              </Table.HeaderCell>
              <Table.HeaderCell width="5" rowSpan="3">
                Title [Provider recid]
              </Table.HeaderCell>

              <Table.HeaderCell collapsing rowSpan="3">
                Action
              </Table.HeaderCell>
              <Table.HeaderCell collapsing rowSpan="3">
                Output document
              </Table.HeaderCell>
              <Table.HeaderCell collapsing colSpan="4">
                Dependent records
              </Table.HeaderCell>
              <Table.HeaderCell collapsing rowSpan="3">
                Partial matches
              </Table.HeaderCell>
              <Table.HeaderCell collapsing rowSpan="3">
                Error
              </Table.HeaderCell>
            </Table.Row>
            <Table.Row>
              <Table.HeaderCell collapsing colSpan="2">
                E-item
              </Table.HeaderCell>
              <Table.HeaderCell collapsing colSpan="2">
                Serials
              </Table.HeaderCell>
            </Table.Row>
            <Table.Row>
              <Table.HeaderCell collapsing>Detected</Table.HeaderCell>
              <Table.HeaderCell collapsing>Action and details</Table.HeaderCell>
              <Table.HeaderCell collapsing>Detected</Table.HeaderCell>
              <Table.HeaderCell collapsing>Details</Table.HeaderCell>
            </Table.Row>
          </Table.Header>
          <Table.Body>
            {records.map((elem, index) => (
              <ImportedDocumentReport
                // Keep the index as key due to lack of other unique id.
                key={index}
                documentReport={elem}
                listIndex={index + (activePage - 1) * pageSize + 1}
              />
            ))}
          </Table.Body>

          <Table.Footer>
            <Table.Row>
              <Table.HeaderCell colSpan="10">
                <Pagination
                  defaultActivePage={1}
                  totalPages={totalPages}
                  activePage={activePage}
                  onPageChange={this.handlePaginationChange}
                  floated="right"
                />
              </Table.HeaderCell>
            </Table.Row>
          </Table.Footer>
        </Table>
        <JsonViewModal />
        <SeriesImportDetailsModal />
        <EitemImportDetailsModal />
      </>
    );
  }
}

ImportedTable.propTypes = {
  records: PropTypes.array.isRequired,
  activePage: PropTypes.number.isRequired,
  onPageChange: PropTypes.func.isRequired,
  pageSize: PropTypes.number.isRequired,
  totalPages: PropTypes.number.isRequired,
};
