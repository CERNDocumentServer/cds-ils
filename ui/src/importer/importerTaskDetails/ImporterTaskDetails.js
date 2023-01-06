import React from "react";
import PropTypes from "prop-types";
import { ImportedDocuments } from "./ImportedDocuments";
import { invenioConfig, withCancel } from "@inveniosoftware/react-invenio-app-ils";
import { importerApi } from "../../api/importer";

export class ImporterTaskDetails extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      data: null,
      isLoading: false,
      error: null,
    };

    this.importCompleted = false;
    this.requestBeingSent = false;
    this.lastEntry = 0;
  }

  componentDidMount() {
    this.intervalId = setInterval(
      // edge case is the request taking longer than the interval time
      // this makes sure it finishes the pending request first
      () => !this.requestBeingSent && this.checkForData(this.taskId),
      invenioConfig.IMPORTER.fetchTaskStatusIntervalSecs
    );
    this.checkForData(this.taskId);
  }

  componentWillUnmount = () => {
    this.intervalId && clearInterval(this.intervalId);
    this.cancellableTaskDetailsFetch && this.cancellableTaskDetailsFetch.cancel();
  };

  get taskId() {
    const {
      match: {
        params: { taskId },
      },
    } = this.props;

    return taskId;
  }

  checkForData = async (taskId) => {
    if (this.importCompleted) {
      this.intervalId && clearInterval(this.intervalId);
      return;
    }

    try {
      this.requestBeingSent = true;

      this.cancellableTaskDetailsFetch = withCancel(
        importerApi.check(taskId, this.lastEntry)
      );

      const { data } = await this.cancellableTaskDetailsFetch.promise;

      this.importCompleted = data.status !== "RUNNING";
      this.lastEntry = data.loaded_entries;

      this.setState((state) => ({
        isLoading: data.status === "RUNNING",
        data: {
          ...state.data,
          ...data,
          records: (state?.data?.records || []).concat(data.records),
        },
      }));
      this.requestBeingSent = false;
    } catch (error) {
      this.requestBeingSent = false;
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
