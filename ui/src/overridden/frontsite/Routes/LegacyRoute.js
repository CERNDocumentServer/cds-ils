import {
  FrontSiteRoutes,
  NotFound,
  recordToPidType,
  withCancel,
} from "@inveniosoftware/react-invenio-app-ils";
import _isEmpty from "lodash/isEmpty";
import PropTypes from "prop-types";
import React from "react";
import { Redirect, Route } from "react-router-dom";
import { Loader } from "semantic-ui-react";
import { legacyApi } from "../../../api/legacy/legacy";
import { FrontSiteRoutes as CdsFrontSiteRoutes } from "../frontsiteUrls";

export const LegacyRecordRoute = () => {
  return (
    <Route
      exact
      path={CdsFrontSiteRoutes.legacyRecordDetails}
      component={LegacyRecordCmp}
    />
  );
};

export class LegacyRecordCmp extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      record: {},
    };
  }

  componentDidMount() {
    const { match } = this.props;
    this.fetchRecordFromLegacyRecId(match.params.legacyRecId);
  }

  componentWillUnmount() {
    this.cancellableFetchRecord && this.cancellableFetchRecord.cancel();
  }

  fetchRecordFromLegacyRecId = async (legacyRecId) => {
    this.cancellableFetchRecord = withCancel(legacyApi.get(legacyRecId));
    const response = await this.cancellableFetchRecord.promise;
    this.setState({ record: response.data });
  };

  render() {
    const { record } = this.state;
    if (_isEmpty(record)) {
      return <Loader active />;
    }
    if (record.id && recordToPidType(record) === "docid") {
      return <Redirect to={FrontSiteRoutes.documentDetailsFor(record.id)} />;
    } else if (record.id && recordToPidType(record) === "serid") {
      return <Redirect to={FrontSiteRoutes.seriesDetailsFor(record.id)} />;
    } else if (record.code === 404) {
      return <NotFound />;
    }
    return null;
  }
}

LegacyRecordCmp.propTypes = {
  match: PropTypes.shape({
    params: PropTypes.shape({
      legacyRecId: PropTypes.string,
    }),
  }).isRequired,
};
