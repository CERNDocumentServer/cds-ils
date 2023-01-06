import { EITEM_DETAILS_MODAL_OPEN, EITEM_DETAILS_MODAL_CLOSE } from "./actions";

export const initialState = {
  open: false,
  eitemReport: {},
};

export const eitemDetailsModalViewReducer = (state = initialState, action) => {
  switch (action.type) {
    case EITEM_DETAILS_MODAL_CLOSE:
      return { ...state, open: false, eitemReport: {} };
    case EITEM_DETAILS_MODAL_OPEN:
      return {
        ...state,
        eitemReport: action.eitemReport,
        open: true,
      };
    default:
      return state;
  }
};
