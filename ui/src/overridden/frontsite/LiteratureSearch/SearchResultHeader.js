import React from "react";
import { Message } from "semantic-ui-react";
import { withState } from "react-searchkit";
import PropTypes from "prop-types";
import { snvLink } from "../../utils";

const SearchResultHeaderCmp = ({ currentQueryState }) => {
  const filters = currentQueryState.filters;

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
