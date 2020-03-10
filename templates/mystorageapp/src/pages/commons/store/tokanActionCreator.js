import {fromJS} from "immutable";
import * as actionType from "./constants"

export const updateToken = (value)=>{
    const action ={
        type:actionType.UPDATE_TOKEN,
        playload:value
    }
    return action;
}