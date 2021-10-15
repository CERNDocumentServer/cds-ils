import React from 'react';
import PropTypes from 'prop-types';
import { Search, Button, Icon } from 'semantic-ui-react';
import debounce from 'lodash/debounce';

export class ImportedSearch extends React.Component {
  constructor(props) {
    super(props);
    this.searchBar = React.createRef();
  }

  componentDidUpdate(prevProps) {
    const { records } = this.props;
    if (prevProps.records !== records) {
      this.newFilter();
    }
  }

  newFilter = () => {
    this.handleSearchChange(this.searchBar.current.state.value);
  };

  handleSearchChange = text => {
    const { records, searchData } = this.props;

    const deb = debounce(text => {
      const searchRecords = records.filter(
        record =>
          record.entry_recid.includes(text) ||
          record.output_pid?.includes(text) ||
          record.document?.title.includes(text) ||
          record.eitem?.output_pid?.includes(text) ||
          record.series?.filter(serie => serie.output_pid?.includes(text))
            .length > 0
      );
      searchData(searchRecords);
    });
    deb(text);
  };

  clearText = () => {
    this.searchBar.current.state.value = '';
    console.log(this.searchBar.current);
    console.log(this.searchBar.current.state);
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
  records: PropTypes.array.isRequired,
  searchData: PropTypes.func.isRequired,
};
