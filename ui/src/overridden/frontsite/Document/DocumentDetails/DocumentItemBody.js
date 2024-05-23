import React from "react";
import {
  DocumentItemBody,
  invenioConfig,
} from "@inveniosoftware/react-invenio-app-ils";
import _get from "lodash/get";
import { parametrize } from "react-overridable";
import { shelfLink, shelfLinkComponent } from "../../../utils";

function renderCallNumber(item) {
  const identifiers = _get(item, "identifiers", []);
  if (identifiers === null) {
    return null;
  }
  const callNumber = identifiers.find(
    (identifier) => identifier.scheme === "CALL_NUMBER"
  );
  if (callNumber) {
    return `(${callNumber.value})`;
  }
  return null;
}

function renderShelflink(item) {
  const shelfNumber = _get(item, "shelf");
  const itemStatus = _get(item, "circulation.state");

  // If item is on loan, don't hyperlink the shelf
  const cannotCirculate =
    invenioConfig.CIRCULATION.loanActiveStates.includes(itemStatus);
  const itemOnShelf = ["CAN_CIRCULATE", "FOR_REFERENCE_ONLY"].includes(
    _get(item, "status")
  );

  const itemShelf =
    cannotCirculate && itemOnShelf
      ? shelfNumber
      : shelfLinkComponent(shelfLink(shelfNumber), shelfNumber);
  return (
    <>
      {itemShelf} {renderCallNumber(item)}
    </>
  );
}

export const DocumentItemBodyTable = parametrize(DocumentItemBody, {
  shelfLink: renderShelflink,
});
