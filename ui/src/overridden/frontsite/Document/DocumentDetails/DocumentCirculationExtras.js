import React, { useRef, useEffect } from "react";
import _get from "lodash/get";
import _isEmpty from "lodash/isEmpty";
import { invenioConfig } from "@inveniosoftware/react-invenio-app-ils";
import { Button, Divider, Icon } from "semantic-ui-react";
import PropTypes from "prop-types";
import { renderCallNumber, shelfLink } from "../../../utils";

// Uses location.replace() so iframe navigation (including server-side redirects)
// doesn't add extra entries to the browser's joint session history.
// eslint-disable-next-line react/prop-types
function MapIframe({ url }) {
  const iframeRef = useRef(null);
  useEffect(() => {
    if (iframeRef.current) {
      iframeRef.current.contentWindow.location.replace(url);
    }
  }, [url]);
  return (
    <div className="ui active embed cern-map">
      <div className="embed">
        <iframe
          ref={iframeRef}
          src="about:blank"
          frameBorder={0}
          allowFullScreen={false}
          scrolling="no"
          width="100%"
          height="100%"
          title="Find it on shelf map"
        />
      </div>
    </div>
  );
}

function canCirculateItem(item) {
  return invenioConfig.ITEMS.canCirculateStatuses.includes(item.status);
}

function isItemForReference(item) {
  return invenioConfig.ITEMS.referenceStatuses.includes(item.status);
}

function getLoanableItem(locations) {
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
    const circulationStatus = _get(item, "circulation.state");
    const itemStatus = _get(item, "status");
    // If item is not on loan and it can be circulated, return item's shelf value
    if (
      !invenioConfig.CIRCULATION.loanActiveStates.includes(circulationStatus) &&
      invenioConfig.ITEMS.canCirculateStatuses.includes(itemStatus)
    ) {
      return item;
    }
  }
  return null;
}

export class DocumentCirculationExtras extends React.Component {
  render() {
    const {
      documentDetails: {
        metadata: {
          title,
          items: { on_shelf: onShelf },
          circulation: { available_items_for_loan_count: availableItems },
        },
      },
    } = this.props;
    if (_isEmpty(onShelf) || availableItems === 0) {
      return null;
    }

    const item = getLoanableItem(onShelf);
    const shelfNumber = _get(item, "shelf");
    if (
      shelfNumber === null ||
      shelfNumber === undefined ||
      isNaN(parseInt(shelfNumber))
    ) {
      // If no item can be loaned, don't display the cernmaps iframe
      return null;
    }
    const popupContent = { "Title": title, "Call number": renderCallNumber(item) };

    return (
      <>
        <Divider />
        <MapIframe url={shelfLink(shelfNumber, { iframe: true })} />
        <Button
          as="a"
          smooth
          href={shelfLink(shelfNumber, { popupContent: popupContent })}
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
