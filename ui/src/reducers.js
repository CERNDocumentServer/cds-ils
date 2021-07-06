import {
  injectAsyncReducer,
  ILSStore,
} from '@inveniosoftware/react-invenio-app-ils';

const jsonModalViewReducer = require('./importer/JsonViewModal/reducer')
  .jsonModalViewReducer;
const seriesDetailsModalViewReducer = require('./importer/SeriesImportDetailsModal/reducer')
  .seriesDetailsModalViewReducer;
const eitemDetailsModalViewReducer = require('./importer/EitemImportDetailsModal/reducer')
  .eitemDetailsModalViewReducer;

export function initialiseReducers() {
  injectAsyncReducer(ILSStore, 'jsonModal', jsonModalViewReducer);
  injectAsyncReducer(
    ILSStore,
    'eitemDetailsModal',
    eitemDetailsModalViewReducer
  );
  injectAsyncReducer(
    ILSStore,
    'seriesDetailsModal',
    seriesDetailsModalViewReducer
  );
}
