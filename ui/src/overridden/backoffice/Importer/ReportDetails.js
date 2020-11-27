import React from 'react';
import PropTypes from 'prop-types';
import { Item, Grid, Message } from 'semantic-ui-react';
import _isEmpty from 'lodash/isEmpty';
import { Link } from 'react-router-dom';
import { BackOfficeRoutes } from '@inveniosoftware/react-invenio-app-ils';
import _get from 'lodash/get';

const displayLinkToDocument = (e, index = 0) => {
  return (
    <Link to={BackOfficeRoutes.documentDetailsFor(e)} target="_blank">
      {index > 0 ? ', ' + e : e}
    </Link>
  );
};

const displayLinkToEitem = (e, index = 0) => {
  return (
    <Link to={BackOfficeRoutes.eitemDetailsFor(e)} target="_blank">
      {index > 0 ? ', ' + e : e}
    </Link>
  );
};

const ReportDetailsLeftColumn = ({ report }) => {
  return (
    <>
      <Item.Description>
        <label>Created: </label>
        {!_isEmpty(report.created_document) ? 'Yes' : 'No'}
      </Item.Description>
      <Item.Description>
        <label>Updated: </label>
        {!_isEmpty(report.updated_document) ? 'Yes' : 'No'}
      </Item.Description>
      <Item.Description>
        <label>Series: </label>
        {!_isEmpty(report.series)
          ? report.series.map((e, index) => (
              <Link
                key={e.pid}
                to={BackOfficeRoutes.seriesDetailsFor(e.pid)}
                target="_blank"
              >
                {index > 0 ? ', ' + e.title : e.title}
              </Link>
            ))
          : 'No'}
      </Item.Description>
    </>
  );
};

ReportDetailsLeftColumn.propTypes = {
  report: PropTypes.object.isRequired,
};

const ReportDetailsMiddleColumn = ({ report }) => {
  return (
    <>
      <Item.Description>
        <label>Ambiguous: </label>
        {!_isEmpty(report.ambiguous_documents)
          ? report.ambiguous_documents.map((e, index) =>
              displayLinkToDocument(e, index)
            )
          : 'No'}
      </Item.Description>
      <Item.Description>
        <label>Fuzzy: </label>
        {!_isEmpty(report.fuzzy_documents)
          ? report.fuzzy_documents.map((e, index) =>
              displayLinkToDocument(e, index)
            )
          : 'No'}
      </Item.Description>
      <Item.Description>
        <label>Ambiguous eitems: </label>
        {!_isEmpty(report.ambiguous_eitems)
          ? report.ambiguous_eitems.map((e, index) =>
              displayLinkToEitem(e, index)
            )
          : 'No'}
      </Item.Description>
    </>
  );
};

ReportDetailsMiddleColumn.propTypes = {
  report: PropTypes.object.isRequired,
};

const ReportDetailsRightColumn = ({ report }) => {
  const deletedEitemsCount = _get(report, 'deleted_eitems.length', 0);
  return (
    <>
      <Item.Description>
        <label>Created eitem: </label>
        {!_isEmpty(report.created_eitem)
          ? displayLinkToEitem(report.created_eitem.pid)
          : 'No'}
      </Item.Description>
      <Item.Description>
        <label>Updated eitem: </label>
        {!_isEmpty(report.updated_eitem)
          ? displayLinkToEitem(report.updated_eitem.pid)
          : 'No'}
      </Item.Description>
      <Item.Description>
        <label>Deleted eitems: </label>
        {deletedEitemsCount}
      </Item.Description>
    </>
  );
};

ReportDetailsRightColumn.propTypes = {
  report: PropTypes.object.isRequired,
};

export class ReportDetails extends React.Component {
  renderErrorMessage = message => {
    return (
      <Message negative>
        <Message.Header>
          Something went wrong while processing this document
        </Message.Header>
        <p>{message}</p>
      </Message>
    );
  };

  render() {
    const { item } = this.props;
    return (
      <Item>
        <Item.Content>
          {item.success ? (
            <Grid columns={3}>
              <Grid.Column>
                <ReportDetailsLeftColumn report={item.report} />
              </Grid.Column>
              <Grid.Column>
                <ReportDetailsMiddleColumn report={item.report} />
              </Grid.Column>
              <Grid.Column>
                <ReportDetailsRightColumn report={item.report} />
              </Grid.Column>
            </Grid>
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
