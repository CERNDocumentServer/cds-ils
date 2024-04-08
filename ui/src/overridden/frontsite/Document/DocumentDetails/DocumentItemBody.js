import React from "react";
import { DocumentItemBody } from "@inveniosoftware/react-invenio-app-ils";
import _get from "lodash/get";
import { parametrize } from "react-overridable";
import { Table } from "semantic-ui-react";

export const DocumentItemTableHeader = () => {
  return (
    <Table.Row data-test="header">
      <Table.HeaderCell>Barcode</Table.HeaderCell>
      <Table.HeaderCell>Shelf</Table.HeaderCell>
      <Table.HeaderCell>Call Number</Table.HeaderCell>
      <Table.HeaderCell>Status</Table.HeaderCell>
      <Table.HeaderCell>Medium</Table.HeaderCell>
      <Table.HeaderCell>Loan restriction</Table.HeaderCell>
    </Table.Row>
  );
};

function renderShelflink(item) {
  const shelfNumber = _get(item, "shelf");
  if (shelfNumber === undefined) return;
  const shelfLink = `https://maps.web.cern.ch/?n=['SHELF ${shelfNumber}']`;
  return (
    <a href={shelfLink} target="_blank" rel="noreferrer">
      {shelfNumber}
    </a>
  );
}

function renderCallNumber(item) {
  const identifiers = _get(item, "identifiers", []);
  if (identifiers === null) {
    return "-";
  }
  const callNumber = identifiers.find(
    (identifier) => identifier.scheme.toLowerCase() === "call number"
  );
  return callNumber ? callNumber.value : "-";
}

export const DocumentItemBodyTable = parametrize(DocumentItemBody, {
  shelfLink: renderShelflink,
  callNumber: renderCallNumber,
});
