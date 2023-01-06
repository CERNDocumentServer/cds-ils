import { IS_LOADING, SUCCESS, HAS_ERROR } from "./actions";

export const initialState = {
  isLoading: true,
  hasError: false,
  data: null,
  error: {},
};

export const vocabularyIdentifiersReducer = (state = initialState, action) => {
  switch (action.type) {
    case IS_LOADING:
      return { ...state, isLoading: true };
    case SUCCESS:
      return { ...state, data: action.payload, isLoading: false };
    case HAS_ERROR:
      return { ...state, hasError: action.payload, isLoading: false };
    default:
      return state;
  }
};
