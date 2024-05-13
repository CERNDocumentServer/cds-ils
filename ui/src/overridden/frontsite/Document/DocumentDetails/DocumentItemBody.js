import React from "react";
import {
  DocumentItemBody,
  InfoPopup,
  invenioConfig,
} from "@inveniosoftware/react-invenio-app-ils";
import _get from "lodash/get";
import { parametrize } from "react-overridable";
import { shelfLink, shelfLinkComponent } from "../../../utils";

function renderCallNumber(item) {
  const identifiers = _get(item, "identifiers", []);
  if (identifiers === null) {
    return "Call number: -";
  }
  const callNumber = identifiers.find(
    (identifier) => identifier.scheme === "CALL_NUMBER"
  );
  return "Call number: " + (callNumber ? callNumber.value : "-");
}

function renderShelflink(item) {
  const shelfNumber = _get(item, "shelf");
  const itemStatus = _get(item, "circulation.state");

  // If item is on loan, don't hyperlink the shelf
  var itemShelf = invenioConfig.CIRCULATION.loanActiveStates.includes(itemStatus)
    ? shelfNumber
    : shelfLinkComponent(shelfLink(shelfNumber), shelfNumber);
  return (
    <InfoPopup message={renderCallNumber(item)}>
      {itemShelf !== undefined ? itemShelf : "-"}
    </InfoPopup>
  );
}

export const DocumentItemBodyTable = parametrize(DocumentItemBody, {
  shelfLink: renderShelflink,
});
