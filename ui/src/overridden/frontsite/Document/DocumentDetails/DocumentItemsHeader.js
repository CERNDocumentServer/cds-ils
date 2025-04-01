import React from "react";
import { Divider, Message } from "semantic-ui-react";
import PropTypes from "prop-types";
import { snvLink } from "../../../utils";

export const DocumentItemsHeader = ({ document }) => {
  return document.metadata.document_type === "STANDARD" ? (
    <>
      <Divider horizontal>Where to find</Divider>
      <Message attached="top" className="warning center">
        <Message.Content>
          To access the standard, follow the link 'e-standard', use your Microsoft 365
          account to log in, and search for the standard on the{" "}
          {snvLink("SNV platform")}.
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
