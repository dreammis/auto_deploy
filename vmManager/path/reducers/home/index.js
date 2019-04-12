import {FETCH_USERNAME} from "Action";

export default (state = {username: null}, action) => {
    switch (action.type) {
        case FETCH_USERNAME:
            return Object.assign({}, state, {username: action.username});
        default:
            return state;
    }
}