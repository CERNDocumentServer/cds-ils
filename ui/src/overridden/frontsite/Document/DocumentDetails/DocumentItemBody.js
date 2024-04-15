import React from "react";
import { DocumentItemBody, InfoPopup } from "@inveniosoftware/react-invenio-app-ils";
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
  if (shelfNumber === undefined) return;
  const itemShelfLink = shelfLink(shelfNumber);
  return (
    <InfoPopup message={renderCallNumber(item)}>
      {shelfLinkComponent(itemShelfLink, shelfNumber)}
    </InfoPopup>
  );
}

export const DocumentItemBodyTable = parametrize(DocumentItemBody, {
  shelfLink: renderShelflink,
});
