import { BackOfficeBase } from "@inveniosoftware/react-invenio-app-ils";
import { generatePath } from "react-router-dom";

export const CdsBackOfficeRoutes = {
  importerCreate: `${BackOfficeBase}/importer`,
  importerDetails: `${BackOfficeBase}/importer/task/:taskId`,
};

export const BackOfficeRouteGenerators = {
  importerDetailsFor: (taskId) =>
    generatePath(CdsBackOfficeRoutes.importerDetails, {
      taskId: taskId,
    }),
};
