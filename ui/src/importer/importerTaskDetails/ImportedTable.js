import React from 'react';
import PropTypes from 'prop-types';
import { Pagination, Table } from 'semantic-ui-react';
import _isEmpty from 'lodash/isEmpty';
import { EitemImportDetailsModal } from '../EitemImportDetailsModal';
import { SeriesImportDetailsModal } from '../SeriesImportDetailsModal';
import { JsonViewModal } from '../JsonViewModal';
import { ImportedDocumentReport } from './ImportedDocumentReport';

export class ImportedTable extends React.Component {
  constructor(props) {
    super(props);
    this.pageSize = 100;
    this.state = {
      activePage: 1,
    };
  }

  componentDidUpdate(prevProps) {
    const { records } = this.props;
    if (prevProps.records !== records) {
      this.resetPage();
    }
  }

  resetPage = () => this.setState({ activePage: 1 });

  handlePaginationChange = (e, { activePage }) => this.setState({ activePage });

  render() {
    const { records } = this.props;
    const { activePage } = this.state;
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
            {records
              .slice(
                activePage * this.pageSize - this.pageSize,
                activePage * this.pageSize
              )
              .map((elem, index) => {
                return (
                  !_isEmpty(elem) && (
                    <ImportedDocumentReport
                      // Keep the index as key due to lack of other unique id.
                      key={index} // eslint-disable-line
                      documentReport={elem}
                      listIndex={index + (activePage - 1) * this.pageSize + 1}
                    />
                  )
                );
              })}
          </Table.Body>

          <Table.Footer>
            <Table.Row>
              <Table.HeaderCell colSpan="10">
                <Pagination
                  defaultActivePage={1}
                  totalPages={Math.ceil(records.length / this.pageSize)}
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
};
