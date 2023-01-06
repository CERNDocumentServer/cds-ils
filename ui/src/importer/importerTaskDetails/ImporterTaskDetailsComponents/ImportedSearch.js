import React from "react";
import PropTypes from "prop-types";
import { Search, Button, Icon } from "semantic-ui-react";
import _debounce from "lodash/debounce";

export class ImportedSearch extends React.Component {
  constructor(props) {
    super(props);
    this.searchBar = React.createRef();
    this.debounceDelay = 250;
  }

  handleSearchChange = (e, { value }) => {
    const { onSearchChange } = this.props;
    onSearchChange(value);
  };

  clearText = () => {
    const { onSearchChange } = this.props;
    this.searchBar.current.state.value = "";
    onSearchChange("");
  };

  render() {
    return (
      <>
        <Search
          className="clean-search"
          onSearchChange={_debounce(this.handleSearchChange, this.debounceDelay)}
          open={false}
          ref={this.searchBar}
          size="large"
        />
        <Button className="center-search-bar-button" icon onClick={this.clearText}>
          <Icon name="times" />
        </Button>
      </>
    );
  }
}

ImportedSearch.propTypes = {
  onSearchChange: PropTypes.func.isRequired,
};
