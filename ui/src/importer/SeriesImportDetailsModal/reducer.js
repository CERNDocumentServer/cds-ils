import { SERIES_DETAILS_MODAL_CLOSE, SERIES_DETAILS_MODAL_OPEN } from "./actions";

export const initialState = {
  open: false,
  seriesReport: [],
};

export const seriesDetailsModalViewReducer = (state = initialState, action) => {
  switch (action.type) {
    case SERIES_DETAILS_MODAL_CLOSE:
      return { ...state, open: false, seriesReport: [] };
    case SERIES_DETAILS_MODAL_OPEN:
      return {
        ...state,
        seriesReport: action.seriesReport,
        open: true,
      };
    default:
      return state;
  }
};
