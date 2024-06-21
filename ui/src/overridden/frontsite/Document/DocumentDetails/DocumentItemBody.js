import React from "react";
import {
  DocumentItemBody,
  invenioConfig,
} from "@inveniosoftware/react-invenio-app-ils";
import _get from "lodash/get";
import { parametrize } from "react-overridable";
import { renderCallNumber, shelfLinkComponent } from "../../../utils";

function renderShelflink(item, documentDetails) {
  const itemStatus = _get(item, "circulation.state");

  // If item is on loan, don't hyperlink the shelf
  const cannotCirculate =
    invenioConfig.CIRCULATION.loanActiveStates.includes(itemStatus);
  const itemOnShelf = ["CAN_CIRCULATE", "FOR_REFERENCE_ONLY"].includes(
    _get(item, "status")
  );

  const shelfNumber = _get(item, "shelf");
  const title = _get(documentDetails, "metadata.title");
  const callNumber = renderCallNumber(item);

  const itemShelf =
    cannotCirculate && itemOnShelf
      ? shelfNumber
      : shelfLinkComponent(shelfNumber, title, callNumber);
  return itemShelf;
}

export const DocumentItemBodyTable = parametrize(DocumentItemBody, {
  shelfLink: renderShelflink,
});
