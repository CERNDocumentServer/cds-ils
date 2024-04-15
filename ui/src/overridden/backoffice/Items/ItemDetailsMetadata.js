import { ItemMetadata } from "@inveniosoftware/react-invenio-app-ils";
import React from "react";
import { parametrize } from "react-overridable";
import _get from "lodash/get";
import _isEmpty from "lodash/isEmpty";
import capitalize from "lodash/capitalize";
import { List } from "semantic-ui-react";
import ShowMore from "react-show-more";
import { getDisplayVal } from "../../utils";

function rightMetadata(itemDetails) {
  const leftColumn = [
    {
      name: "Status",
      value: getDisplayVal("ITEMS.statuses", itemDetails.metadata.status),
    },
    {
      name: "Loan restrictions",
      value: getDisplayVal(
        "ITEMS.circulationRestrictions",
        itemDetails.metadata.circulation_restriction
      ),
    },
    {
      name: "Description",
      value: (
        <ShowMore
          lines={5}
          more="Show more"
          less="Show less"
          anchorClass="button-show-more"
        >
          {itemDetails.metadata.description || "-"}
        </ShowMore>
      ),
    },
    {
      name: "Internal notes",
      value: (
        <ShowMore
          lines={5}
          more="Show more"
          less="Show less"
          anchorClass="button-show-more"
        >
          {itemDetails.metadata.internal_notes || "-"}
        </ShowMore>
      ),
    },
  ];
  const itemIdentifiers = itemDetails.metadata.identifiers;
  if (!_isEmpty(itemIdentifiers)) {
    leftColumn.push({
      name: "Identifiers",
      value: (
        <List bulleted>
          {itemIdentifiers.map((entry) => (
            <List.Item key={entry.value}>
              <List.Content>
                {entry.value + " (" + capitalize(entry.scheme).replace("_", " ") + ")"}
              </List.Content>
            </List.Item>
          ))}
        </List>
      ),
    });
  }
  return leftColumn;
}

export const ItemDetailsMetadata = parametrize(ItemMetadata, {
  rightMetadataColumn: rightMetadata,
});
