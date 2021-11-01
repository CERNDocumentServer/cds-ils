import React from 'react';
import PropTypes from 'prop-types';
import { ImportedDocuments } from './ImportedDocuments';
import { invenioConfig } from '@inveniosoftware/react-invenio-app-ils';
import _get from 'lodash/get';
import { importerApi } from '../../api/importer';

export class ImporterTaskDetails extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      data: null,
      isLoading: false,
      error: null,
      importCompleted: false,
    };
  }

  componentDidMount() {
    this.intervalId = setInterval(
      () => this.checkForData(this.taskId),
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

  checkForData = async () => {
    const { importCompleted, data } = this.state;

    if (importCompleted) {
      this.intervalId && clearInterval(this.intervalId);
      return;
    }
    try {
      const nextEntry = _get(data, 'loaded_entries', 0);
      const response = await importerApi.check(this.taskId, nextEntry);
      if (response.data.status !== 'RUNNING') {
        this.setState({
          importCompleted: true,
          isLoading: false,
          data: response.data,
        });
      } else {
        this.setState({
          isLoading: true,
          data: response.data,
        });
      }
    } catch (error) {
      this.setState({ error, isLoading: false });
    }
  };

  render() {
    const { data, isLoading, error } = this.state;

    return (
      <ImportedDocuments
        data={data}
        isLoading={isLoading}
        error={error}
        taskId={this.taskId}
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
