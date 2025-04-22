import React from "react";
import { Divider, Message } from "semantic-ui-react";
import PropTypes from "prop-types";

export const DocumentItemsHeader = ({ document }) => {
  return document.metadata.document_type === "STANDARD" ? (
    <>
      <Divider horizontal>Where to find</Divider>
      <Message attached="top" className="warning center">
        <Message.Content>
          To access e-standards, follow the{" "}
          <a
            href="https://sis.web.cern.ch/search-and-read/online-resources/snv-connect"
            target="_blank"
            rel="noopener noreferrer"
          >
            instructions
          </a>
          . IEEE standards are available via{" "}
          <a
            href="https://ieeexplore-ieee-org.ezproxy.cern.ch/Xplore/home.jsp"
            target="_blank"
            rel="noopener noreferrer"
          >
            IEEE Xplore
          </a>
          .
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
