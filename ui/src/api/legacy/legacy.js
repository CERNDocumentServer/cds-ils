import { http } from "@inveniosoftware/react-invenio-app-ils";

const legacyRecordURL = "/legacy/";

const get = async (legacyRecId) => {
  const response = await http.get(`${legacyRecordURL}${legacyRecId}`);
  return response;
};

export const legacyApi = {
  get: get,
};
