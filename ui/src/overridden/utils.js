import React from "react";
import { invenioConfig } from "@inveniosoftware/react-invenio-app-ils";
import { Icon } from "semantic-ui-react";

export const snvLink = (
  <a
    href="https://sis.web.cern.ch/search-and-read/online-resources/snv-connect"
    target="_blank"
    rel="noreferrer"
  >
    SNV-Connect
  </a>
);

export const shelfLink = (shelfNumber, iframe = false) => {
  var shelfLink = `https://maps.web.cern.ch/?n=['SHELF ${shelfNumber}']`;
  if (iframe) {
    shelfLink = `${shelfLink}&showMenu=false&widgets=&scale=125`;
  }
  return shelfLink;
};

export const shelfLinkComponent = (
  shelfLink,
  shelfNumber,
  iconName = "map marker alternate"
) => {
  return (
    <a href={shelfLink} target="_blank" rel="noreferrer">
      <Icon name={iconName} />
      {shelfNumber}
    </a>
  );
};

export function getDisplayVal(configField, value) {
  return _get(invenioConfig, configField).find((entry) => entry.value === value).text;
}
