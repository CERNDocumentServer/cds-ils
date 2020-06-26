import { FrontSiteRoutes } from '@inveniosoftware/react-invenio-app-ils';
import Qs from 'qs';
import React from 'react';
import { Link } from 'react-router-dom';
import { Dropdown, Menu, Responsive } from 'semantic-ui-react';
import { config } from '../../../config';

const onClickBookRequestLink = () => {
  const params = Qs.parse(window.location.search);
  const queryString = params['?q'];
  return {
    pathname: FrontSiteRoutes.documentRequestForm,
    state: { queryString },
  };
};

const dropdownEntries = (
  <Dropdown.Menu>
    <Dropdown.Item as="a" href="https://library.web.cern.ch/resources/remote">
      External Online <br /> Resources
    </Dropdown.Item>
    <Dropdown.Divider />
    <Dropdown.Item as="a" href="#">
      F.A.Q.
    </Dropdown.Item>
    <Dropdown.Divider />
    <Dropdown.Item as="a" href={`mailto:${config.uiConfig.library_email}`}>
      Ask a librarian
    </Dropdown.Item>
    <Dropdown.Divider />
    <Dropdown.Item as={Link} to={onClickBookRequestLink()}>
      Request new <br /> literature
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
