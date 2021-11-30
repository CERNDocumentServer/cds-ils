import React from 'react';
import PropTypes from 'prop-types';
import { ImportedDocuments } from './ImportedDocuments';
import { invenioConfig } from '@inveniosoftware/react-invenio-app-ils';
import { importerApi } from '../../api/importer';

export class ImporterTaskDetails extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      data: null,
      isLoading: false,
      isImporting: false,
      error: null,
    };

    this.queryParams = {
      page: 1,
      pageSize: 100,
      filterType: 'all',
    };

    this.importCompleted = false;
    this.requestBeingSent = false;
  }

  componentDidMount() {
    const { isLoading } = this.state;
    this.intervalId = setInterval(
      // edge case is the request taking longer than the interval time
      // this makes sure it finishes the pending request first
      () => !isLoading && this.checkForData(this.taskId, false),
      invenioConfig.IMPORTER.fetchTaskStatusIntervalSecs
    );

    this.checkForData(this.taskId);
  }

  componentWillUnmount = () => {
    this.intervalId && clearInterval(this.intervalId);
  };

  get taskId() {
    const {
      match: {
        params: { taskId },
      },
    } = this.props;

    return taskId;
  }

  checkForData = async (taskId, force = true) => {
    if (this.importCompleted && !force) {
      this.intervalId && clearInterval(this.intervalId);
      return;
    }

    try {
      const { page, pageSize, filterType } = this.queryParams;

      if (force) {
        this.setState({
          isLoading: true,
        });
      }

      const { data } = await importerApi.check(taskId, {
        page,
        page_size: pageSize,
        filter_type: filterType,
      });

      this.setState({
        isImporting: data.status === 'RUNNING',
        isLoading: false,
        data,
      });

      this.importCompleted = data.status !== 'RUNNING';
    } catch (error) {
      this.requestBeingSent = false;
      this.setState({ error, isLoading: false });
    }
  };

  setFilter = key => {
    this.queryParams = { ...this.queryParams, page: 1, filterType: key };

    this.checkForData(this.taskId);
  };

  setActivePage = page => {
    this.queryParams.page = page;

    this.checkForData(this.taskId);
  };

  render() {
    const { data, isLoading, error, isImporting } = this.state;
    const { page, pageSize, filterType } = this.queryParams;

    return (
      <ImportedDocuments
        data={data}
        isImporting={isImporting}
        isLoading={isLoading}
        error={error}
        taskId={this.taskId}
        page={page}
        pageSize={pageSize}
        filterType={filterType}
        setPage={this.setActivePage}
        setFilterType={this.setFilter}
      />
    );
  }
}

ImporterTaskDetails.propTypes = {
  match: PropTypes.shape({
    params: PropTypes.shape({
      taskId: PropTypes.string,
    }),
  }).isRequired,
};
