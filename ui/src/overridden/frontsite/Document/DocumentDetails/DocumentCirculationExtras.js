import React from "react";
import _get from "lodash/get";
import _isEmpty from "lodash/isEmpty";
import { invenioConfig } from "@inveniosoftware/react-invenio-app-ils";
import { Embed, Button, Divider, Icon } from "semantic-ui-react";
import PropTypes from "prop-types";
import { shelfLink } from "../../../utils";

function canCirculateItem(item) {
  return invenioConfig.ITEMS.canCirculateStatuses.includes(item.status);
}

function isItemForReference(item) {
  return invenioConfig.ITEMS.referenceStatuses.includes(item.status);
}

function getLoanableItemShelf(locations) {
  const locationEntries = Object.entries(locations);
  if (_isEmpty(locationEntries)) return {};

  var allRelevantItems = [];

  locationEntries.forEach(([locationName, internalLocations]) => {
    const internalLocationEntries = Object.entries(internalLocations);

    internalLocationEntries.forEach(([internalLocationName, items]) => {
      if (internalLocationName === "total") return;

      const relevantItems = items.filter(
        (item) => canCirculateItem(item) || isItemForReference(item)
      );
      allRelevantItems = allRelevantItems.concat(relevantItems);
    });
  });

  for (const item of allRelevantItems) {
    const itemStatus = _get(item, "circulation.state");
    // If item is not on loan, return item's shelf value
    if (!invenioConfig.CIRCULATION.loanActiveStates.includes(itemStatus)) {
      return item.shelf;
    }
  }
  return null;
}

export class DocumentCirculationExtras extends React.Component {
  render() {
    const {
      documentDetails: {
        metadata: {
          items: { on_shelf: onShelf },
          circulation: { available_items_for_loan_count: availableItems },
        },
      },
    } = this.props;
    if (_isEmpty(onShelf) || availableItems === 0) {
      return null;
    }

    const shelfNumber = getLoanableItemShelf(onShelf);
    if (
      shelfNumber === null ||
      shelfNumber === undefined ||
      isNaN(parseInt(shelfNumber))
    ) {
      // If no item can be loaned, don't display the cernmaps iframe
      return null;
    }

    return (
      <>
        <Divider />
        <Embed className="cern-map" active url={shelfLink(shelfNumber, true)} />
        <Button
          as="a"
          smooth
          href={shelfLink(shelfNumber)}
          target="_blank"
          rel="noreferrer"
          color="blue"
          fluid
          icon
          labelPosition="left"
        >
          <Icon name="map pin" />
          Find it on shelf
        </Button>
      </>
    );
  }
}

DocumentCirculationExtras.propTypes = {
  documentDetails: PropTypes.object.isRequired,
};