import React from "react";
import { Message } from "semantic-ui-react";
import { Link } from "react-router-dom";
import { withState } from "react-searchkit";
import PropTypes from "prop-types";

const SearchResultHeaderCmp = ({ currentQueryState }) => {
  const snvLink = (
    <Link
      href="https://sis.web.cern.ch/search-and-read/online-resources/snv-connect"
      taget="_blank"
    >
      SNV-Connect
    </Link>
  );

  const filters = currentQueryState.filters;

  console.log("test", currentQueryState);
  return filters.some((item) => item.includes("STANDARD")) ? (
    <Message attached="top" className="warning center">
      <Message.Content>
        For standards, please directly search on {snvLink}.
      </Message.Content>
    </Message>
  ) : (
    ""
  );
};

SearchResultHeaderCmp.propTypes = {
  currentQueryState: PropTypes.object.isRequired,
};

export const SearchResultHeader = withState(SearchResultHeaderCmp);
