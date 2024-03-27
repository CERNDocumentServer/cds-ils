import React from "react";
import { Header } from "semantic-ui-react";
import { FrontSiteRoutes } from "@inveniosoftware/react-invenio-app-ils";
import { Link } from "react-router-dom";

export const DocumentRequestFormHeader = () => {
  return (
    <>
      <Header as="h1">Request document</Header>
      <p>
        Fill in the form below to request to loan, purchase or suggest a document (book,
        article, standard, etc.) to the Library.
      </p>
      <p>
        We will do our best to give you access to e-books, but please note that not all
        books are made available as e-books by providers.
      </p>
      <p>
        You can see all your requests on your{" "}
        <Link to={FrontSiteRoutes.patronProfile}>profile</Link> page.
      </p>
    </>
  );
};
