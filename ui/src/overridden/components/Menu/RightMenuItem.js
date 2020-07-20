import { FrontSiteRoutes } from '@inveniosoftware/react-invenio-app-ils';
import React from 'react';
import { Link } from 'react-router-dom';
import { Dropdown, Menu, Responsive } from 'semantic-ui-react';
import { config } from '../../../config';

const dropdownEntries = (
  <Dropdown.Menu>
    <Dropdown.Item as="a" href="https://library.web.cern.ch/resources/remote">
      External Online Resources
    </Dropdown.Item>
    <Dropdown.Divider />
    <Dropdown.Item as="a" href="#">
      F.A.Q.
    </Dropdown.Item>
    <Dropdown.Divider />
    <Dropdown.Item as="a" href={`mailto:${config.libraryEmail}`}>
      Ask a librarian
    </Dropdown.Item>
    <Dropdown.Divider />
    <Dropdown.Item as={Link} to={FrontSiteRoutes.documentRequestForm}>
      Request new literature
    </Dropdown.Item>
  </Dropdown.Menu>
);

export const RightMenuItem = ({ ...props }) => {
  return (
    <Menu.Item>
      <Responsive minWidth={Responsive.onlyTablet.minWidth}>
        <Dropdown item text="Help" icon="caret down">
          {dropdownEntries}
        </Dropdown>
      </Responsive>
    </Menu.Item>
  );
};

export const RightMenuItemMobile = ({ ...props }) => {
  return (
    <Responsive {...Responsive.onlyMobile}>
      <Dropdown item icon="help">
        {dropdownEntries}
      </Dropdown>
    </Responsive>
  );
};
