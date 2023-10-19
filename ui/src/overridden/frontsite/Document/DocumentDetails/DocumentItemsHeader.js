import React from "react";
import { Divider, Message } from "semantic-ui-react";
import PropTypes from "prop-types";
import { snvLink } from "../../utils";

export const DocumentItemsHeader = ({ document }) => {
  return document.metadata.document_type === "STANDARD" ? (
    <>
      <Divider horizontal>Where to find</Divider>
      <Message attached="top" className="warning center">
        <Message.Content>
          For standards, please directly search on {snvLink}. Please contact
          library.desk@cern.ch in case you cannot find what you are looking for.
        </Message.Content>
      </Message>
    </>
  ) : (
    ""
  );
};

DocumentItemsHeader.propTypes = {
  document: PropTypes.object.isRequired,
};
