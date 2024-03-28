import React from "react";
import { Menu } from "semantic-ui-react";
import { CdsBackOfficeRoutes } from "../../routes/BackofficeUrls";
import PropTypes from "prop-types";
import { Link } from "react-router-dom";
import { BackOfficeRoutes } from "@inveniosoftware/react-invenio-app-ils";

export class SideBarMenuItem extends React.Component {
  render() {
    const { activePath } = this.props;
    const importerActive = activePath.includes(CdsBackOfficeRoutes.importerCreate);

    return (
      <Menu.Item>
        <Menu.Header>Importer</Menu.Header>
        <Menu.Menu>
          <Menu.Item
            as={importerActive ? "" : Link}
            active={importerActive}
            to={CdsBackOfficeRoutes.importerCreate}
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

export class SideBarCatalogueItem extends React.Component {
  render() {
    const { activePath } = this.props;

    const documentsActive = activePath.includes(BackOfficeRoutes.documentsList);
    const seriesActive = activePath.includes(BackOfficeRoutes.seriesList);
    const itemsActive = activePath.includes(BackOfficeRoutes.itemsList);
    const eitemsActive = activePath.includes(BackOfficeRoutes.eitemsList);

    return (
      <Menu.Item>
        <Menu.Header>Catalogue</Menu.Header>
        <Menu.Menu>
          <Menu.Item
            as={Link}
            active={documentsActive}
            to={BackOfficeRoutes.documentsList}
          >
            Books / Articles
          </Menu.Item>
          <Menu.Item as={Link} active={seriesActive} to={BackOfficeRoutes.seriesList}>
            Series / Multiparts
          </Menu.Item>
          <Menu.Item as={Link} active={itemsActive} to={BackOfficeRoutes.itemsList}>
            Physical Copies
          </Menu.Item>
          <Menu.Item as={Link} active={eitemsActive} to={BackOfficeRoutes.eitemsList}>
            E-Items
          </Menu.Item>
        </Menu.Menu>
      </Menu.Item>
    );
  }
}

SideBarCatalogueItem.propTypes = {
  activePath: PropTypes.string.isRequired,
};
