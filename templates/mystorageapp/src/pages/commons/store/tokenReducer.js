import { fromJS } from "immutable";
import * as actionType from "./constants"

let initState={
    "value":"",
};

export default function tokenReducer(state=initState, action) {
    switch (action.type) {
        case  actionType.UPDATE_TOKEN:
            return {"value":action.playload};
        default:
            return state;
    }
}
