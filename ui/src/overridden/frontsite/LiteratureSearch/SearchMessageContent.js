import React from "react";
import { Message } from "semantic-ui-react";
import { FrontSiteRoutes } from "@inveniosoftware/react-invenio-app-ils";
import { Link } from "react-router-dom";
import Qs from "qs";

export const SearchMessageContent = () => {
  const onClickBookRequestLink = () => {
    const params = Qs.parse(window.location.search);
    const queryString = params["?q"];
    return {
      pathname: FrontSiteRoutes.documentRequestForm,
      state: { queryString },
    };
  };
  const requestFormLink = (
    <Link className="primary" to={onClickBookRequestLink()}>
      request form
    </Link>
  );
  return (
    <Message.Content>
      <Message.Header>Couldn't find the document you were looking for?</Message.Header>
      Please fill in the {requestFormLink} to request a new document from the library.
      (Login required)
    </Message.Content>
  );
};
