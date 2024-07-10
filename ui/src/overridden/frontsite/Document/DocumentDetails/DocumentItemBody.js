import React from "react";
import {
  DocumentItemBody,
  invenioConfig,
  InfoPopup,
} from "@inveniosoftware/react-invenio-app-ils";
import _get from "lodash/get";
import _isEmpty from "lodash/isEmpty";
import { parametrize } from "react-overridable";
import { renderCallNumber, shelfLinkComponent } from "../../../utils";

function renderShelflink(item, documentDetails) {
  const itemStatus = _get(item, "circulation.state");

  // If item is not on loan, hyperlink the shelf
  const canCirculateItem =
    !invenioConfig.CIRCULATION.loanActiveStates.includes(itemStatus);
  const itemIsOnShelf = ["CAN_CIRCULATE", "FOR_REFERENCE_ONLY"].includes(
    _get(item, "status")
  );

  const shelfNumber = _get(item, "shelf");
  const title = _get(documentDetails, "metadata.title");
  var callNumber = renderCallNumber(item);

  const itemShelf =
    canCirculateItem && itemIsOnShelf && !_isEmpty(shelfNumber)
      ? shelfLinkComponent(shelfNumber, title, callNumber)
      : shelfNumber;

  if (_isEmpty(shelfNumber)) {
    // If shelfNumber is empty, show info popup regardless of availability
    callNumber = (
      <InfoPopup message="Please request online or ask at the Library desk.">
        {" "}
        {callNumber}
      </InfoPopup>
    );
  }

  return (
    <>
      {itemShelf} {callNumber}
    </>
  );
}

export const DocumentItemBodyTable = parametrize(DocumentItemBody, {
  shelfLink: renderShelflink,
});
