import React from 'react';
import PropTypes from 'prop-types';
import { ImportedDocuments } from './ImportedDocuments';

export class ImporterTaskDetails extends React.Component {
  render() {
    const {
      match: {
        params: { taskId },
      },
    } = this.props;
    return <ImportedDocuments taskId={taskId} />;
  }
}

ImporterTaskDetails.propTypes = {
  match: PropTypes.shape({
    params: PropTypes.shape({
      taskId: PropTypes.string,
    }),
  }).isRequired,
};
