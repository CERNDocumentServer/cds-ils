import {
  FrontSiteRoutes,
  getStaticPageByName,
  Media,
} from "@inveniosoftware/react-invenio-app-ils";
import React from "react";
import { Link } from "react-router-dom";
import { Dropdown, Menu } from "semantic-ui-react";

const DropdownItems = () => {
  return (
    <>
      <Dropdown.Item as={Link} to={getStaticPageByName("faq").route}>
        Frequently asked questions (F.A.Q.)
      </Dropdown.Item>
      <Dropdown.Divider />
      <Dropdown.Item as={Link} to={getStaticPageByName("search-guide").route}>
        Search guide
      </Dropdown.Item>
      <Dropdown.Divider />
      <Dropdown.Item as={Link} to={FrontSiteRoutes.documentRequestForm}>
        Request document (loan or purchase)
      </Dropdown.Item>
      <Dropdown.Divider />
      <Dropdown.Item as={Link} to={getStaticPageByName("contact").route}>
        Ask a librarian
      </Dropdown.Item>
      <Dropdown.Divider />
      <Dropdown.Item
        as="a"
        href="https://mattermost.web.cern.ch/sis-team/channels/library-requests"
      >
        Contact
      </Dropdown.Item>
      <Dropdown.Divider />
      <Dropdown.Item as={Link} to={FrontSiteRoutes.openingHours}>
        Opening hours
      </Dropdown.Item>
      <Dropdown.Divider />
      <Dropdown.Item as="a" href="https://library.web.cern.ch/resources/remote">
        Remote access to e-resources
      </Dropdown.Item>
      <Dropdown.Divider />
      <Dropdown.Item
        as="a"
        href="https://scientific-info.cern/search-and-read/online-resources"
      >
        CERN Library online resources
      </Dropdown.Item>
    </>
  );
};

export const RightMenuItem = () => {
  return (
    <Menu.Item>
      <Media greaterThanOrEqual="computer">
        <Dropdown item text="Help" icon="caret down">
          <Dropdown.Menu>
            <DropdownItems />
          </Dropdown.Menu>
        </Dropdown>
      </Media>
    </Menu.Item>
  );
};

export const RightMenuItemMobile = () => {
  return (
    <Media lessThan="computer">
      <Dropdown item icon="help">
        <Dropdown.Menu>
          <DropdownItems />
        </Dropdown.Menu>
      </Dropdown>
    </Media>
  );
};
