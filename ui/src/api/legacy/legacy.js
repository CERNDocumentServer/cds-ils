import { http } from '@inveniosoftware/react-invenio-app-ils';

const legacyDocumentURL = '/legacy/';

const get = async legacyRecId => {
  const response = await http.get(`${legacyDocumentURL}${legacyRecId}`);
  return response;
};

export const legacyApi = {
  get: get,
};
