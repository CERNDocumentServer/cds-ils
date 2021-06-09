import React from 'react';
import PropTypes from 'prop-types';
import { Item, Icon, Table, Message } from 'semantic-ui-react';
import _isEmpty from 'lodash/isEmpty';
import { Link } from 'react-router-dom';
import { BackOfficeRoutes } from '@inveniosoftware/react-invenio-app-ils';

const displayRecordLink = (id, label) => (
  <Link to={id} target="_blank">
    {label}
  </Link>
);

const displayValue = (value, urlGenerator, getId, getTitle) => {
  return _isEmpty(value)
    ? ''
    : displayRecordLink(urlGenerator(getId(value)), getTitle(value));
};

const displayValues = (values, urlGenerator, getId, getTitle) => {
  return _isEmpty(values)
    ? ''
    : values.map((value, index) => (
        <span key={index}>
          {index > 0 ? ', ' : ''}
          {displayValue(value, urlGenerator, getId, getTitle)}
        </span>
      ));
};

export class ReportDetails extends React.Component {
  renderErrorMessage = message => {
    let title;
    let content;
    const split = message.split(': ');
    if (split.length > 1 && split[0] === 'LossyConversion') {
      title = 'Lossy conversion detected';
      content = `The literature was not imported because conversion rules for some of the fields were not available. This concerns the following fields: ${split[1]}`;
    } else {
      title = 'Something went wrong while processing this document';
      content = `An unexpected error was encountered: ${message}`;
    }
    return (
      <Message negative>
        <Message.Header>{title}</Message.Header>
        <p>{content}</p>
      </Message>
    );
  };

  getRows = () => {
    const { item } = this.props;
    if (!item.success) {
      return [];
    }
    return [
      {
        icon: 'plus',
        name: 'Created',
        documents: displayValue(
          item.created_document,
          BackOfficeRoutes.documentDetailsFor,
          o => o.pid,
          o => o.title
        ),
        eitems: displayValue(
          item.created_eitem,
          BackOfficeRoutes.eitemDetailsFor,
          o => o.pid,
          o => o.pid
        ),
        series: null,
      },
      {
        icon: 'edit',
        name: 'Updated',
        documents: displayValue(
          item.updated_document,
          BackOfficeRoutes.documentDetailsFor,
          o => o.pid,
          o => o.title
        ),
        eitems: displayValue(
          item.updated_eitem,
          BackOfficeRoutes.eitemDetailsFor,
          o => o.pid,
          o => o.pid
        ),
        series: displayValues(
          item.series,
          BackOfficeRoutes.seriesDetailsFor,
          o => o.pid,
          o => o.title
        ),
      },
      {
        icon: 'minus',
        name: 'Deleted',
        documents: null,
        eitems: displayValues(
          item.deleted_eitems,
          BackOfficeRoutes.eitemDetailsFor,
          o => o.pid,
          o => o.pid
        ),
        series: null,
      },
      {
        icon: 'magic',
        name: 'Fuzzy',
        documents: displayValues(
          item.fuzzy_documents,
          BackOfficeRoutes.documentDetailsFor,
          o => o,
          o => o
        ),
        eitems: null,
        series: null,
      },
      {
        icon: 'question',
        name: 'Ambiguous',
        documents: displayValues(
          item.ambiguous_documents,
          BackOfficeRoutes.documentDetailsFor,
          o => o,
          o => o
        ),
        eitems: null,
        series: null,
      },
    ];
  };

  render() {
    const { item } = this.props;
    return (
      <Item>
        <Item.Content>
          {item.success ? (
            <Table definition compact striped textAlign="center">
              <Table.Header>
                <Table.Row>
                  <Table.HeaderCell />
                  <Table.HeaderCell>Documents</Table.HeaderCell>
                  <Table.HeaderCell>E-Items</Table.HeaderCell>
                  <Table.HeaderCell>Series</Table.HeaderCell>
                </Table.Row>
              </Table.Header>
              <Table.Body>
                {this.getRows().map(row => (
                  <Table.Row key={row.name}>
                    <Table.Cell collapsing textAlign="left">
                      <Icon name={row.icon} />
                      {row.name}
                    </Table.Cell>
                    <Table.Cell>{row.documents}</Table.Cell>
                    <Table.Cell>{row.eitems}</Table.Cell>
                    <Table.Cell>{row.series}</Table.Cell>
                  </Table.Row>
                ))}
              </Table.Body>
            </Table>
          ) : (
            this.renderErrorMessage(item.message)
          )}
        </Item.Content>
      </Item>
    );
  }
}

ReportDetails.propTypes = {
  item: PropTypes.object.isRequired,
};
