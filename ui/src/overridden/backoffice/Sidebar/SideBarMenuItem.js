import React from 'react';
import { Menu } from 'semantic-ui-react';
import { CdsBackOfficeRoutes } from '../../routes/BackofficeUrls';
import PropTypes from 'prop-types';
import { Link } from 'react-router-dom';

export class SideBarMenuItem extends React.Component {
  render() {
    const { activePath } = this.props;
    const importerActive = activePath.includes(CdsBackOfficeRoutes.importer);

    return (
      <Menu.Item>
        <Menu.Header>Importer</Menu.Header>
        <Menu.Menu>
          <Menu.Item
            as={importerActive ? '' : Link}
            active={importerActive}
            to={CdsBackOfficeRoutes.importer}
          >
            Import
          </Menu.Item>
        </Menu.Menu>
      </Menu.Item>
    );
  }
}

SideBarMenuItem.propTypes = {
  activePath: PropTypes.string.isRequired,
};
