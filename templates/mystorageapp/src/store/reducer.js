import {combineReducers} from "redux";
import tokenReducer from "../pages/commons/store/tokenReducer";

export default combineReducers(
    {
        token:tokenReducer,
    }
)
