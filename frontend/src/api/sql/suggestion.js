import axios from '../../libs/http';

const suggestion = '/api/sqlmng/suggestion/';

export function GetSuggestionList(params) {
    return axios({
        url: suggestion,
        method: 'get',
        params
    });
}

export function CreateSuggestion(data) {
    return axios({
        url: suggestion,
        method: 'post',
        data: data
    });
}

export function DeleteSuggestion(id) {
    return axios({
        url: suggestion + id + '/',
        method: 'delete',
    });
}