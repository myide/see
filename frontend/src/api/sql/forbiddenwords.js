import axios from '../../libs/http';

const forbiddenwords = '/api/sqlmng/forbiddenwords/';

export function GetFWList(params) {
    return axios({
        url: forbiddenwords,
        method: 'get',
        params
    });
}

export function UpdateFW(id, data) {
    return axios({
        url: forbiddenwords + id + '/',
        method: 'put',
        data: data
    });
}

export function CreateFW(data) {
    return axios({
        url: forbiddenwords,
        method: 'post',
        data: data
    });
}