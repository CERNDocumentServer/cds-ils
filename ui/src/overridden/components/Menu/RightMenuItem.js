import {
  FrontSiteRoutes,
  getStaticPageByName,
  invenioConfig,
} from '@inveniosoftware/react-invenio-app-ils';
import React from 'react';
import { Link } from 'react-router-dom';
import { Dropdown, Menu, Responsive } from 'semantic-ui-react';

const DropdownItems = () => {
  return (
    <>
      <Dropdown.Item as="a" href="https://library.web.cern.ch/resources/remote">
        External Online Resources
      </Dropdown.Item>
      <Dropdown.Divider />
      <Dropdown.Item as={Link} to={getStaticPageByName('faq').route}>
        F.A.Q.
      </Dropdown.Item>
      <Dropdown.Divider />
      <Dropdown.Item as="a" href={`mailto:${invenioConfig.APP.libraryEmail}`}>
        Ask a librarian
      </Dropdown.Item>
      <Dropdown.Divider />
      <Dropdown.Item as={Link} to={FrontSiteRoutes.documentRequestForm}>
        Request new literature
      </Dropdown.Item>
    </>
  );
};

export const RightMenuItem = () => {
  return (
    <Menu.Item>
      <Responsive minWidth={Responsive.onlyTablet.minWidth}>
        <Dropdown item text="Help" icon="caret down">
          <Dropdown.Menu>
            <DropdownItems />
          </Dropdown.Menu>
        </Dropdown>
      </Responsive>
    </Menu.Item>
  );
};

export const RightMenuItemMobile = () => {
  return (
    <Responsive {...Responsive.onlyMobile}>
      <Dropdown item icon="help">
        <Dropdown.Menu>
          <DropdownItems />
        </Dropdown.Menu>
      </Dropdown>
    </Responsive>
  );
};
