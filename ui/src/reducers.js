import { injectAsyncReducer, ILSStore } from "@inveniosoftware/react-invenio-app-ils";

const jsonModalViewReducer =
  require("./importer/JsonViewModal/reducer").jsonModalViewReducer;
const seriesDetailsModalViewReducer =
  require("./importer/SeriesImportDetailsModal/reducer").seriesDetailsModalViewReducer;
const eitemDetailsModalViewReducer =
  require("./importer/EitemImportDetailsModal/reducer").eitemDetailsModalViewReducer;

const vocabularyIdentifiersReducer =
  require("./overridden/frontsite/Document/DocumentDetails/DocumentMetadataTabs/Identifiers/reducer").vocabularyIdentifiersReducer;

export function initialiseReducers() {
  injectAsyncReducer(ILSStore, "jsonModal", jsonModalViewReducer);
  injectAsyncReducer(ILSStore, "eitemDetailsModal", eitemDetailsModalViewReducer);
  injectAsyncReducer(ILSStore, "seriesDetailsModal", seriesDetailsModalViewReducer);
  injectAsyncReducer(ILSStore, "vocabularyIdentifiers", vocabularyIdentifiersReducer);
}
