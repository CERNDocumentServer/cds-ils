import React from 'react';
import PropTypes from 'prop-types';
import { Search, Button, Icon } from 'semantic-ui-react';

export class ImportedSearch extends React.Component {
  constructor(props) {
    super(props);
    this.searchBar = React.createRef();
  }

  handleSearchChange = text => {
    const { setSearchText } = this.props;
    setSearchText(text);
  };

  clearText = () => {
    this.searchBar.current.state.value = '';
    this.handleSearchChange('');
  };

  render() {
    return (
      <>
        <Search
          className="clean-search"
          onSearchChange={(event, text) => this.handleSearchChange(text.value)}
          open={false}
          ref={this.searchBar}
          size="large"
        />
        <Button
          className="center-search-bar-button"
          icon
          onClick={(event, data) => this.clearText()}
        >
          <Icon name="times" />
        </Button>
      </>
    );
  }
}

ImportedSearch.propTypes = {
  setSearchText: PropTypes.func.isRequired,
};
