import { JSON_MODAL_CLOSE, JSON_MODAL_OPEN } from "./actions";

export const initialState = {
  open: false,
  title: "JSON View",
  json: {},
};

export const jsonModalViewReducer = (state = initialState, action) => {
  switch (action.type) {
    case JSON_MODAL_CLOSE:
      return { ...state, open: false, title: "JSON View", json: {} };
    case JSON_MODAL_OPEN:
      return {
        ...state,
        isLoading: false,
        title: action.title,
        json: action.json,
        open: true,
      };
    default:
      return state;
  }
};
