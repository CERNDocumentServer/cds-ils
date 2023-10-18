import React from "react";
import { Divider, Message } from "semantic-ui-react";
import { Link } from "react-router-dom";
import PropTypes from "prop-types";

export const DocumentItemsHeader = ({ document }) => {
  const snvLink = (
    <Link
      href="https://sis.web.cern.ch/search-and-read/online-resources/snv-connect"
      taget="_blank"
    >
      SNV-Connect
    </Link>
  );
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
