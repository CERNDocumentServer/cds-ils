import React from "react";
import PropTypes from "prop-types";
import { Button, Grid, Icon } from "semantic-ui-react";
import { Link } from "react-router-dom";
import { CdsBackOfficeRoutes } from "../../../overridden/routes/BackofficeUrls";
import { ImportedSearch } from "./ImportedSearch";
import { CancelImportTask } from "./cancelImportTask";

export class ImporterReportHeader extends React.Component {
  render() {
    const { isLoadingFile, isImporting, taskId, onSearch } = this.props;

    return (
      <Grid>
        <Grid.Column floated="left" width={12}>
          <Button
            className="default-margin-top"
            labelPosition="left"
            icon="left arrow"
            content="Import other files"
            loading={isLoadingFile}
            disabled={isLoadingFile}
            as={Link}
            to={CdsBackOfficeRoutes.importerCreate}
          />
          {isImporting && (
            <>
              <CancelImportTask logId={taskId} /> <Icon loading name="circle notch" />
              This may take a while. You may leave the page, the process will continue
              in background.
            </>
          )}
        </Grid.Column>
        <Grid.Column textAlign="right" floated="right" width={4}>
          <ImportedSearch onSearchChange={onSearch} />
        </Grid.Column>
      </Grid>
    );
  }
}

ImporterReportHeader.propTypes = {
  isImporting: PropTypes.bool.isRequired,
  taskId: PropTypes.string.isRequired,
  onSearch: PropTypes.func.isRequired,
  isLoadingFile: PropTypes.bool.isRequired,
};
