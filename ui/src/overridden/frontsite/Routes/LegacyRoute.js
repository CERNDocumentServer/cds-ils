import { FrontSiteRoutes as CdsFrontSiteRoutes } from '../frontsiteUrls';
import {
  NotFound,
  withCancel,
  DocumentDetails,
} from '@inveniosoftware/react-invenio-app-ils';
import { Switch, Route } from 'react-router-dom';
import React from 'react';
import PropTypes from 'prop-types';
import { legacyApi } from '../../../api/legacy/legacy';

export const LegacyDocumentRoute = ({ ...props }) => {
  return (
    <Switch>
      <Route
        exact
        path={CdsFrontSiteRoutes.legacyDocumentDetails}
        component={LegacyDocumentCmp}
      />
      <Route>
        <NotFound />
      </Route>
    </Switch>
  );
};

export class LegacyDocumentCmp extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      data: {},
    };
  }

  componentDidMount() {
    const { match } = this.props;
    this.fetchDocumentFromLegacyRecId(match.params.legacyRecId);
  }

  componentWillUnmount() {
    this.cancellableFetchDocument && this.cancellableFetchDocument.cancel();
  }

  fetchDocumentFromLegacyRecId = async legacyRecId => {
    this.cancellableFetchDocument = withCancel(legacyApi.get(legacyRecId));
    const response = await this.cancellableFetchDocument.promise;
    this.setState({ data: response.data });
  };

  render() {
    const { data } = this.state;
    if (data.id) {
      window.history.pushState({ data }, '', '/literature/' + data.id);
      return <DocumentDetails documentDetails={data} />;
    } else if (data.code === 404) {
      return <NotFound />;
    }
    return null;
  }
}

LegacyDocumentCmp.propTypes = {
  match: PropTypes.shape({
    params: PropTypes.shape({
      legacyRecId: PropTypes.string,
    }),
  }).isRequired,
};
