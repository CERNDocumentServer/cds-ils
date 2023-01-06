import { http } from "@inveniosoftware/react-invenio-app-ils";

const importerURL = "/importer";
const headers = {
  headers: {
    "Content-Type": "multipart/form-data",
  },
};
const createTask = async (formData) => {
  return await http.post(`${importerURL}`, formData, headers);
};

const check = async (taskId, nextEntry = 0) => {
  return await http.get(`${importerURL}/${taskId}/offset/${nextEntry}`);
};

const list = async () => {
  return await http.get(`${importerURL}`);
};

const cancel = async (taskId) => {
  return await http.post(`${importerURL}/${taskId}/cancel`);
};

export const importerApi = {
  check: check,
  cancel: cancel,
  createTask: createTask,
  list: list,
  url: importerURL,
};
